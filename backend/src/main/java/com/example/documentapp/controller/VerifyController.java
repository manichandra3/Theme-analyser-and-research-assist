package com.example.documentapp.controller;

import com.example.documentapp.dto.VerifyRequest;
import com.example.documentapp.dto.VerifyResponse;
import com.example.documentapp.service.VerificationService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class VerifyController {

  private final VerificationService verificationService;

  VerifyController(VerificationService verificationService) {
    this.verificationService = verificationService;
  }

  @PostMapping("/api/verify")
  public VerifyResponse verify(@Valid @RequestBody VerifyRequest request) {
    return verificationService.verify(request);
  }
}