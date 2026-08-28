package com.example.documentapp.service;

import com.example.documentapp.dto.VerifyRequest;
import com.example.documentapp.dto.VerifyResponse;
import org.springframework.stereotype.Service;

@Service
public class VerificationService {

  private final VerificationPipeline pipeline;

  public VerificationService(VerificationPipeline pipeline) {
    this.pipeline = pipeline;
  }

  public VerifyResponse verify(VerifyRequest request) {
    return pipeline.execute(request);
  }
}