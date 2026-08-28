package com.example.documentapp.service;

import com.example.documentapp.config.AppProperties;
import com.example.documentapp.dto.VerifyRequest;
import com.google.genai.Client;
import com.google.genai.types.GenerateContentConfig;
import com.google.genai.types.GenerateContentResponse;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

@Component
public class GeminiGroundednessJudge implements GroundednessJudge {

  private static final Logger log = LoggerFactory.getLogger(GeminiGroundednessJudge.class);

  private static final String GROUNDEDNESS_PROMPT = """
      You are a strict groundedness evaluator. Judge whether the ANSWER is fully supported
      by the provided CONTEXT CHUNKS.

      CONTEXT CHUNKS:
      {context}

      ANSWER:
      {answer}

      Return ONLY a JSON object:
      {
        "score": 0.0_to_1.0,
        "explanation": "brief explanation of the score"
      }
      """;

  private final Client client;
  private final String model;
  private final double threshold;

  public GeminiGroundednessJudge(AppProperties properties) {
    this.model = properties.geminiModel();
    this.threshold = properties.groundednessThreshold();
    String apiKey = properties.geminiApiKey();
    if (apiKey != null && !apiKey.isBlank()) {
      this.client = Client.builder().apiKey(apiKey).build();
    } else {
      log.warn("Gemini API key not configured, GeminiGroundednessJudge will return -1.0");
      this.client = null;
    }
  }

  @Override
  public double score(String answer, List<VerifyRequest.ChunkRef> chunks) {
    if (client == null) {
      return -1.0;
    }

    if (answer == null || answer.isBlank() || chunks.isEmpty()) {
      return 0.0;
    }

    try {
      String context = buildContext(chunks);
      String prompt = GROUNDEDNESS_PROMPT
          .replace("{context}", context)
          .replace("{answer}", answer);

      GenerateContentConfig config = GenerateContentConfig.builder()
          .temperature(0.0f)
          .maxOutputTokens(256)
          .build();

      GenerateContentResponse response = client.models.generateContent(model, prompt, config);
      String responseText = response.text();

      if (responseText != null) {
        return parseScore(responseText);
      }
    } catch (Exception e) {
      log.error("Gemini groundedness evaluation failed: {}", e.getMessage());
    }

    return -1.0;
  }

  private String buildContext(List<VerifyRequest.ChunkRef> chunks) {
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < chunks.size(); i++) {
      VerifyRequest.ChunkRef chunk = chunks.get(i);
      sb.append(String.format("[Chunk %d - Doc: %s, Page: %d, Para: %d]\n%s\n\n",
          i + 1, chunk.docId(), chunk.page(), chunk.paragraph(), chunk.content()));
    }
    return sb.toString();
  }

  private double parseScore(String responseText) {
    try {
      int start = responseText.indexOf('{');
      int end = responseText.lastIndexOf('}');
      if (start >= 0 && end > start) {
        String json = responseText.substring(start, end + 1);
        var parser = new com.google.gson.JsonParser();
        var jsonObject = parser.parse(json).getAsJsonObject();
        if (jsonObject.has("score")) {
          double score = jsonObject.get("score").getAsDouble();
          return Math.max(0.0, Math.min(1.0, score));
        }
      }
    } catch (Exception e) {
      log.debug("Failed to parse Gemini response: {}", responseText);
    }
    return -1.0;
  }
}