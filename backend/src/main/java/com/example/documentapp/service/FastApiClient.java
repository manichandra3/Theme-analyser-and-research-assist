package com.example.documentapp.service;

import com.example.documentapp.dto.*;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;
import java.util.List;
import java.util.Map;

@Service
public class FastApiClient {

  private final WebClient webClient;

  public FastApiClient(WebClient fastApiWebClient) {
    this.webClient = fastApiWebClient;
  }

  public Mono<DocumentUploadResponse> uploadDocument(byte[] fileBytes, String filename, String contentType) {
    return webClient.post()
        .uri("/api/v1/upload")
        .contentType(MediaType.MULTIPART_FORM_DATA)
        .body(BodyInserters.fromMultipartData("file", new org.springframework.core.io.ByteArrayResource(fileBytes) {
          @Override
          public String getFilename() {
            return filename;
          }
        }))
        .retrieve()
        .bodyToMono(DocumentUploadResponse.class)
        .onErrorResume(e -> Mono.just(new DocumentUploadResponse(false, "Upload failed: " + e.getMessage(), null, null)));
  }

  public Mono<List<SearchResult>> searchDocuments(String query, int k, String mode) {
    return webClient.get()
        .uri(uriBuilder -> uriBuilder.path("/api/v1/search")
            .queryParam("query", query)
            .queryParam("k", k)
            .queryParam("mode", mode)
            .build())
        .retrieve()
        .bodyToMono(new org.springframework.core.ParameterizedTypeReference<List<SearchResult>>() {})
        .onErrorResume(e -> Mono.just(List.of()));
  }

  public Mono<AskResponse> askQuestion(String question, int k) {
    return webClient.get()
        .uri(uriBuilder -> uriBuilder.path("/api/v1/ask")
            .queryParam("question", question)
            .queryParam("k", k)
            .build())
        .retrieve()
        .bodyToMono(AskResponse.class)
        .onErrorResume(e -> Mono.just(new AskResponse(List.of())));
  }

  public Mono<RetrievalEvalResponse> evaluateRetrieval(List<RetrievalTestCase> testCases, int evalK) {
    RetrievalEvalRequest request = new RetrievalEvalRequest(testCases, evalK);
    return webClient.post()
        .uri("/api/v1/evaluate/retrieval")
        .bodyValue(request)
        .retrieve()
        .bodyToMono(RetrievalEvalResponse.class)
        .onErrorResume(e -> Mono.just(new RetrievalEvalResponse(Map.of(), List.of())));
  }

  public Mono<GenerationEvalResponse> evaluateGeneration(List<GenerationTestCase> testCases, int finalK) {
    GenerationEvalRequest request = new GenerationEvalRequest(testCases, finalK);
    return webClient.post()
        .uri("/api/v1/evaluate/generation")
        .bodyValue(request)
        .retrieve()
        .bodyToMono(GenerationEvalResponse.class)
        .onErrorResume(e -> Mono.just(new GenerationEvalResponse(List.of())));
  }

  public Mono<List<DocumentSummary>> listDocuments() {
    return webClient.get()
        .uri("/api/v1/documents")
        .retrieve()
        .bodyToMono(new org.springframework.core.ParameterizedTypeReference<List<DocumentSummary>>() {})
        .onErrorResume(e -> Mono.just(List.of()));
  }

  public Mono<DocumentDetails> getDocumentDetails(int documentId) {
    return webClient.get()
        .uri("/api/v1/documents/{documentId}", documentId)
        .retrieve()
        .bodyToMono(DocumentDetails.class)
        .onErrorResume(e -> Mono.empty());
  }

  public Mono<DeleteResponse> deleteDocument(int documentId) {
    return webClient.delete()
        .uri("/api/v1/documents/{documentId}", documentId)
        .retrieve()
        .bodyToMono(DeleteResponse.class)
        .onErrorResume(e -> Mono.just(new DeleteResponse(false, "Delete failed: " + e.getMessage())));
  }

  public Mono<DeleteResponse> clearAllDocuments() {
    return webClient.delete()
        .uri("/api/v1/clear-all")
        .retrieve()
        .bodyToMono(DeleteResponse.class)
        .onErrorResume(e -> Mono.just(new DeleteResponse(false, "Clear failed: " + e.getMessage())));
  }
}