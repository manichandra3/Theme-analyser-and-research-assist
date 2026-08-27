package com.example.documentapp.service;

import com.example.documentapp.config.AppProperties;
import com.example.documentapp.dto.VerifyRequest.ChunkRef;
import java.util.List;
import org.springframework.stereotype.Component;

@Component
class GeminiGroundednessJudge implements GroundednessJudge {

  private final AppProperties properties;

  GeminiGroundednessJudge(AppProperties properties) {
    this.properties = properties;
  }

  @Override
  public double score(String answer, List<ChunkRef> chunks) {
    return -1.0;
  }
}