package com.example.documentapp.service;

import com.example.documentapp.config.AppProperties;
import com.example.documentapp.dto.VerifyResponse;
import java.util.ArrayList;
import java.util.List;
import org.springframework.stereotype.Component;

@Component
public class DefaultVerificationPolicy implements VerificationPolicy {

  private final double threshold;

  public DefaultVerificationPolicy(AppProperties properties) {
    this.threshold = properties.groundednessThreshold();
  }

  @Override
  public String determineVerdict(double groundednessScore, List<VerifyResponse.CitationCheck> citations) {
    boolean allCitationsResolved = citations.stream().allMatch(VerifyResponse.CitationCheck::resolved);
    boolean meetsThreshold = groundednessScore >= threshold;

    if (meetsThreshold && allCitationsResolved) {
      return "PASS";
    } else if (!meetsThreshold && !allCitationsResolved) {
      return "FAIL";
    } else if (!meetsThreshold) {
      return "LOW_GROUNDEDNESS";
    } else {
      return "UNRESOLVED_CITATIONS";
    }
  }

  @Override
  public List<String> collectIssues(double groundednessScore, List<VerifyResponse.CitationCheck> citations) {
    List<String> issues = new ArrayList<>();

    if (groundednessScore < threshold) {
      issues.add(String.format("Groundedness score %.2f below threshold %.2f", groundednessScore, threshold));
    }

    long unresolvedCount = citations.stream()
        .filter(c -> !c.resolved())
        .count();
    if (unresolvedCount > 0) {
      issues.add(String.format("%d unresolved citation(s)", unresolvedCount));
    }

    citations.stream()
        .filter(c -> c.supportScore() < 0.5)
        .forEach(c -> issues.add(String.format("Weak support for citation '%s': %.2f", c.citation(), c.supportScore())));

    return issues;
  }
}