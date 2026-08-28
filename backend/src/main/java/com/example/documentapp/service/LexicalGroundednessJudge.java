package com.example.documentapp.service;

import com.example.documentapp.dto.VerifyRequest;
import java.util.*;
import java.util.stream.Collectors;
import org.springframework.stereotype.Component;

@Component
public class LexicalGroundednessJudge implements GroundednessJudge {

  private static final Set<String> STOP_WORDS = Set.of(
      "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
      "of", "with", "by", "from", "as", "is", "was", "are", "were", "been",
      "be", "have", "has", "had", "do", "does", "did", "will", "would", "could",
      "should", "may", "might", "must", "can", "this", "that", "these", "those",
      "it", "its", "their", "them", "they", "we", "you", "your", "our", "us",
      "i", "me", "my", "mine", "he", "him", "his", "she", "her", "hers"
  );

  @Override
  public double score(String answer, List<VerifyRequest.ChunkRef> chunks) {
    if (answer == null || answer.isBlank() || chunks.isEmpty()) {
      return 0.0;
    }

    Map<String, Double> answerTfIdf = computeTfIdf(answer, chunks);
    Map<String, Double> contextTfIdf = computeContextTfIdf(chunks);

    return cosineSimilarity(answerTfIdf, contextTfIdf);
  }

  private Map<String, Double> computeTfIdf(String text, List<VerifyRequest.ChunkRef> chunks) {
    Map<String, Integer> termFreq = new HashMap<>();
    String[] words = tokenize(text);

    for (String word : words) {
      if (!STOP_WORDS.contains(word) && word.length() > 2) {
        termFreq.merge(word, 1, Integer::sum);
      }
    }

    int totalTerms = words.length;
    Map<String, Double> tfIdf = new HashMap<>();

    for (Map.Entry<String, Integer> entry : termFreq.entrySet()) {
      String term = entry.getKey();
      double tf = (double) entry.getValue() / totalTerms;
      double idf = computeIdf(term, chunks);
      tfIdf.put(term, tf * idf);
    }

    return tfIdf;
  }

  private Map<String, Double> computeContextTfIdf(List<VerifyRequest.ChunkRef> chunks) {
    Map<String, Integer> termFreq = new HashMap<>();
    int totalTerms = 0;

    for (VerifyRequest.ChunkRef chunk : chunks) {
      if (chunk.content() != null) {
        String[] words = tokenize(chunk.content());
        for (String word : words) {
          if (!STOP_WORDS.contains(word) && word.length() > 2) {
            termFreq.merge(word, 1, Integer::sum);
            totalTerms++;
          }
        }
      }
    }

    Map<String, Double> tfIdf = new HashMap<>();
    int numChunks = chunks.size();

    for (Map.Entry<String, Integer> entry : termFreq.entrySet()) {
      String term = entry.getKey();
      double tf = (double) entry.getValue() / totalTerms;
      double idf = Math.log((double) numChunks / (1 + countChunksWithTerm(term, chunks)));
      tfIdf.put(term, tf * idf);
    }

    return tfIdf;
  }

  private double computeIdf(String term, List<VerifyRequest.ChunkRef> chunks) {
    int count = countChunksWithTerm(term, chunks);
    return Math.log((double) chunks.size() / (1 + count));
  }

  private int countChunksWithTerm(String term, List<VerifyRequest.ChunkRef> chunks) {
    return (int) chunks.stream()
        .filter(chunk -> chunk.content() != null && chunk.content().toLowerCase().contains(term))
        .count();
  }

  private String[] tokenize(String text) {
    return text.toLowerCase().split("\\W+");
  }

  private double cosineSimilarity(Map<String, Double> vec1, Map<String, Double> vec2) {
    Set<String> allTerms = new HashSet<>();
    allTerms.addAll(vec1.keySet());
    allTerms.addAll(vec2.keySet());

    if (allTerms.isEmpty()) return 0.0;

    double dotProduct = 0.0;
    double norm1 = 0.0;
    double norm2 = 0.0;

    for (String term : allTerms) {
      double v1 = vec1.getOrDefault(term, 0.0);
      double v2 = vec2.getOrDefault(term, 0.0);
      dotProduct += v1 * v2;
      norm1 += v1 * v1;
      norm2 += v2 * v2;
    }

    if (norm1 == 0.0 || norm2 == 0.0) return 0.0;

    return dotProduct / (Math.sqrt(norm1) * Math.sqrt(norm2));
  }

  public double supportScore(String claim, VerifyRequest.ChunkRef chunk) {
    if (claim == null || chunk.content() == null) return 0.0;

    String[] claimWords = tokenize(claim);
    String[] chunkWords = tokenize(chunk.content());

    Set<String> claimSet = Arrays.stream(claimWords)
        .filter(w -> w.length() > 2 && !STOP_WORDS.contains(w))
        .collect(Collectors.toSet());

    Set<String> chunkSet = Arrays.stream(chunkWords)
        .filter(w -> w.length() > 2 && !STOP_WORDS.contains(w))
        .collect(Collectors.toSet());

    if (claimSet.isEmpty() || chunkSet.isEmpty()) return 0.0;

    int originalSize = claimSet.size();
    claimSet.retainAll(chunkSet);
    return (double) claimSet.size() / originalSize;
  }
}