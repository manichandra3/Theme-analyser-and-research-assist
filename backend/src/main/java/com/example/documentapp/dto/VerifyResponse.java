package com.example.documentapp.dto;

import java.util.List;

public record VerifyResponse(
    String verdict,
    double groundednessScore,
    List<CitationCheck> citations,
    List<String> issues) {

  public record CitationCheck(
      String citation,
      boolean resolved,
      double supportScore,
      String status) {
  }
}