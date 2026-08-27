package com.example.documentapp.service;

import com.example.documentapp.config.AppProperties;
import com.example.documentapp.dto.VerifyRequest;
import com.example.documentapp.dto.VerifyResponse;
import org.springframework.stereotype.Service;

@Service
public class VerificationService {

  private final CitationValidator citationValidator;
  private final LexicalGroundednessJudge lexicalJudge;
  private final GeminiGroundednessJudge geminiJudge;
  private final AppProperties properties;

  VerificationService(CitationValidator citationValidator,
      LexicalGroundednessJudge lexicalJudge,
      GeminiGroundednessJudge geminiJudge,
      AppProperties properties) {
    this.citationValidator = citationValidator;
    this.lexicalJudge = lexicalJudge;
    this.geminiJudge = geminiJudge;
    this.properties = properties;
  }

  public VerifyResponse verify(VerifyRequest request) {
    return null;
  }
}