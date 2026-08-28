package com.example.documentapp.service;

import com.example.documentapp.dto.*;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Mono;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class RagPipelineIntegrationService {

  private final FastApiClient fastApiClient;
  private final VerificationService verificationService;

  public RagPipelineIntegrationService(FastApiClient fastApiClient, VerificationService verificationService) {
    this.fastApiClient = fastApiClient;
    this.verificationService = verificationService;
  }

  public Mono<VerifiedAskResponse> askWithVerification(String question, int k) {
    return fastApiClient.askQuestion(question, k)
        .flatMap(askResponse -> {
          var verificationRequest = buildVerificationRequest(question, askResponse);
          return Mono.fromCallable(() -> verificationService.verify(verificationRequest))
              .map(verificationResponse -> new VerifiedAskResponse(askResponse, verificationResponse));
        });
  }

  public Mono<VerifiedSearchResponse> searchWithVerification(String query, int k, String mode) {
    return fastApiClient.searchDocuments(query, k, mode)
        .flatMap(searchResults -> {
          var verificationRequest = buildSearchVerificationRequest(query, searchResults);
          return Mono.fromCallable(() -> verificationService.verify(verificationRequest))
              .map(verificationResponse -> new VerifiedSearchResponse(searchResults, verificationResponse));
        });
  }

  public Mono<VerifiedGenerationEvalResponse> evaluateGenerationWithVerification(
      List<GenerationTestCase> testCases, int finalK) {
    return fastApiClient.evaluateGeneration(testCases, finalK)
        .flatMap(genResponse -> {
          var verificationRequest = buildGenerationVerificationRequest(testCases, genResponse);
          return Mono.fromCallable(() -> verificationService.verify(verificationRequest))
              .map(verificationResponse -> new VerifiedGenerationEvalResponse(genResponse, verificationResponse));
        });
  }

  private VerifyRequest buildVerificationRequest(String question, AskResponse askResponse) {
    var chunks = askResponse.items().stream()
        .filter(item -> item.docId() != null && !item.docId().equals("Answer"))
        .map(item -> new VerifyRequest.ChunkRef(item.docId(), 0, 0, item.content()))
        .collect(Collectors.toList());
    return new VerifyRequest(question, "", chunks);
  }

  private VerifyRequest buildSearchVerificationRequest(String query, List<SearchResult> results) {
    var chunks = results.stream()
        .map(result -> new VerifyRequest.ChunkRef(
            (String) result.metadata().getOrDefault("doc_id", "unknown"),
            0, 0, result.text()))
        .collect(Collectors.toList());
    return new VerifyRequest(query, "", chunks);
  }

  private VerifyRequest buildGenerationVerificationRequest(
      List<GenerationTestCase> testCases, GenerationEvalResponse genResponse) {
    var chunks = genResponse.results().stream()
        .filter(result -> result.metrics() != null)
        .map(result -> new VerifyRequest.ChunkRef(result.question(), 0, 0, result.answer()))
        .collect(Collectors.toList());
    return new VerifyRequest("Generation Evaluation", "", chunks);
  }

  public record VerifiedAskResponse(
      AskResponse askResponse,
      VerifyResponse verificationResponse
  ) {}

  public record VerifiedSearchResponse(
      List<SearchResult> searchResults,
      VerifyResponse verificationResponse
  ) {}

  public record VerifiedGenerationEvalResponse(
      GenerationEvalResponse generationResponse,
      VerifyResponse verificationResponse
  ) {}
}