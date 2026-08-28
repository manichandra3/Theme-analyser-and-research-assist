package com.example.documentapp.service;

import com.example.documentapp.config.AppProperties;
import org.springframework.stereotype.Component;

@Component
public class GroundednessJudgeFactory {

  private final LexicalGroundednessJudge lexicalJudge;
  private final GeminiGroundednessJudge geminiJudge;
  private final AppProperties properties;

  public GroundednessJudgeFactory(LexicalGroundednessJudge lexicalJudge,
      GeminiGroundednessJudge geminiJudge,
      AppProperties properties) {
    this.lexicalJudge = lexicalJudge;
    this.geminiJudge = geminiJudge;
    this.properties = properties;
  }

  public GroundednessJudge createJudge() {
    if (properties.geminiApiKey() != null && !properties.geminiApiKey().isBlank()) {
      return new FallbackGroundednessJudge(geminiJudge, lexicalJudge);
    }
    return lexicalJudge;
  }

  public GroundednessJudge createLexicalOnly() {
    return lexicalJudge;
  }
}