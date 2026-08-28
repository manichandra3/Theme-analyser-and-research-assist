package com.example.documentapp.controller;

import com.example.documentapp.dto.*;
import com.example.documentapp.service.RagPipelineIntegrationService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;
import java.util.List;

@RestController
@RequestMapping("/api/rag")
public class RagPipelineController {

  private final RagPipelineIntegrationService ragPipelineService;

  public RagPipelineController(RagPipelineIntegrationService ragPipelineService) {
    this.ragPipelineService = ragPipelineService;
  }

  @GetMapping("/ask")
  public Mono<RagPipelineIntegrationService.VerifiedAskResponse> askWithVerification(
      @RequestParam String question,
      @RequestParam(defaultValue = "5") int k) {
    return ragPipelineService.askWithVerification(question, k);
  }

  @GetMapping("/search")
  public Mono<RagPipelineIntegrationService.VerifiedSearchResponse> searchWithVerification(
      @RequestParam String query,
      @RequestParam(defaultValue = "5") int k,
      @RequestParam(defaultValue = "hybrid") String mode) {
    return ragPipelineService.searchWithVerification(query, k, mode);
  }

  @PostMapping("/evaluate/generation")
  public Mono<RagPipelineIntegrationService.VerifiedGenerationEvalResponse> evaluateGenerationWithVerification(
      @Valid @RequestBody GenerationEvalRequest request) {
    return ragPipelineService.evaluateGenerationWithVerification(request.testCases(), request.finalK());
  }
}