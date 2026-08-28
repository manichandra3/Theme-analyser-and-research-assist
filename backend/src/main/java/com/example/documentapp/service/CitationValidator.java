package com.example.documentapp.service;

import com.example.documentapp.dto.VerifyRequest;
import com.example.documentapp.dto.VerifyResponse;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.springframework.stereotype.Component;

@Component
public class CitationValidator {

  private static final Pattern CITATION_PATTERN = Pattern.compile(
      "\\[([^\\]]+)\\]|\\(([^)]+)\\)|\\{([^}]+)\\}|(?:doc|page|para)[\\s:_-]*(\\w+)");

  private static final Pattern DOC_ID_PATTERN = Pattern.compile("(\\w+)_p(\\d+)_c(\\d+)");

  public List<Citation> extract(String answer) {
    List<Citation> citations = new ArrayList<>();
    if (answer == null || answer.isBlank()) {
      return citations;
    }

    Matcher matcher = CITATION_PATTERN.matcher(answer);
    while (matcher.find()) {
      String raw = matcher.group(0);
      String content = matcher.group(1) != null ? matcher.group(1)
          : matcher.group(2) != null ? matcher.group(2)
              : matcher.group(3) != null ? matcher.group(3)
                  : matcher.group(4);

      Optional<String> docId = parseDocId(content);
      docId.ifPresent(id -> citations.add(new Citation(id, 0, 0, raw)));
    }

    return citations;
  }

  public List<VerifyResponse.CitationCheck> resolve(
      List<Citation> citations, List<VerifyRequest.ChunkRef> chunks) {
        List<VerifyResponse.CitationCheck> results = new ArrayList<>();

    for (Citation citation : citations) {
      Optional<VerifyRequest.ChunkRef> matchingChunk = chunks.stream()
          .filter(chunk -> citation.docId().equals(chunk.docId()))
          .findFirst();

      boolean resolved = matchingChunk.isPresent();
      double supportScore = matchingChunk.map(chunk -> calculateSupport(citation.raw(), chunk.content()))
          .orElse(0.0);

      String status = resolved
          ? (supportScore >= 0.5 ? "SUPPORTED" : "WEAK_SUPPORT")
          : "UNRESOLVED";

      results.add(new VerifyResponse.CitationCheck(
          citation.raw(), resolved, supportScore, status));
    }

    return results;
  }

  private double calculateSupport(String citation, String chunkContent) {
    if (citation == null || chunkContent == null) return 0.0;

    String[] citationWords = citation.toLowerCase().split("\\W+");
    String[] chunkWords = chunkContent.toLowerCase().split("\\W+");

    if (citationWords.length == 0 || chunkWords.length == 0) return 0.0;

    int matches = 0;
    for (String cw : citationWords) {
      if (cw.length() > 2) {
        for (String chw : chunkWords) {
          if (chw.contains(cw) || cw.contains(chw)) {
            matches++;
            break;
          }
        }
      }
    }

    return (double) matches / citationWords.length;
  }

  private Optional<String> parseDocId(String content) {
    Matcher matcher = DOC_ID_PATTERN.matcher(content);
    if (matcher.find()) {
      return Optional.of(matcher.group(0));
    }
    return Optional.empty();
  }
}