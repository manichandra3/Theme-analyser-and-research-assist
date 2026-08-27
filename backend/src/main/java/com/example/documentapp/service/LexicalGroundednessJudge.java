package com.example.documentapp.service;

import com.example.documentapp.dto.VerifyRequest.ChunkRef;
import java.util.List;
import org.springframework.stereotype.Component;

@Component
class LexicalGroundednessJudge implements GroundednessJudge {

  @Override
  public double score(String answer, List<ChunkRef> chunks) {
    return 0.0;
  }

  double supportScore(String claim, ChunkRef chunk) {
    return 0.0;
  }
}