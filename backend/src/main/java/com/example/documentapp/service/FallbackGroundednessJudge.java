package com.example.documentapp.service;

import com.example.documentapp.dto.VerifyRequest;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class FallbackGroundednessJudge implements GroundednessJudge {

  private static final Logger log = LoggerFactory.getLogger(FallbackGroundednessJudge.class);

  private final GroundednessJudge primary;
  private final GroundednessJudge fallback;

  public FallbackGroundednessJudge(GroundednessJudge primary, GroundednessJudge fallback) {
    this.primary = primary;
    this.fallback = fallback;
  }

  @Override
  public double score(String answer, List<VerifyRequest.ChunkRef> chunks) {
    double primaryScore = primary.score(answer, chunks);

    if (primaryScore >= 0.0) {
      return primaryScore;
    }

    log.warn("Primary judge failed, falling back to lexical judge");
    return fallback.score(answer, chunks);
  }
}