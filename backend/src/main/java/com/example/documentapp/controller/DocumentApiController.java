package com.example.documentapp.controller;

import com.example.documentapp.dto.*;
import com.example.documentapp.service.FastApiClient;
import jakarta.validation.Valid;
import org.springframework.http.MediaType;
import org.springframework.http.codec.multipart.FilePart;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;

@RestController
@RequestMapping("/api")
public class DocumentApiController {

  private final FastApiClient fastApiClient;

  public DocumentApiController(FastApiClient fastApiClient) {
    this.fastApiClient = fastApiClient;
  }

  @PostMapping(value = "/upload", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
  public Mono<DocumentUploadResponse> uploadDocument(
      @RequestPart("file") FilePart filePart) {
    return filePart.content()
        .map(dataBuffer -> {
          byte[] bytes = new byte[dataBuffer.readableByteCount()];
          dataBuffer.read(bytes);
          return bytes;
        })
        .reduce((a, b) -> {
          byte[] combined = new byte[a.length + b.length];
          System.arraycopy(a, 0, combined, 0, a.length);
          System.arraycopy(b, 0, combined, a.length, b.length);
          return combined;
        })
        .flatMap(bytes -> fastApiClient.uploadDocument(bytes, filePart.filename(), filePart.headers().getContentType().toString()));
  }

  @GetMapping("/search")
  public Mono<java.util.List<SearchResult>> searchDocuments(
      @RequestParam String query,
      @RequestParam(defaultValue = "5") int k,
      @RequestParam(defaultValue = "hybrid") String mode) {
    return fastApiClient.searchDocuments(query, k, mode);
  }

  @GetMapping("/ask")
  public Mono<AskResponse> askQuestion(
      @RequestParam String question,
      @RequestParam(defaultValue = "5") int k) {
    return fastApiClient.askQuestion(question, k);
  }

  @PostMapping("/evaluate/retrieval")
  public Mono<RetrievalEvalResponse> evaluateRetrieval(
      @Valid @RequestBody RetrievalEvalRequest request) {
    return fastApiClient.evaluateRetrieval(request.testCases(), request.evalK());
  }

  @PostMapping("/evaluate/generation")
  public Mono<GenerationEvalResponse> evaluateGeneration(
      @Valid @RequestBody GenerationEvalRequest request) {
    return fastApiClient.evaluateGeneration(request.testCases(), request.finalK());
  }

  @GetMapping("/documents")
  public Mono<java.util.List<DocumentSummary>> listDocuments() {
    return fastApiClient.listDocuments();
  }

  @GetMapping("/documents/{documentId}")
  public Mono<DocumentDetails> getDocument(@PathVariable int documentId) {
    return fastApiClient.getDocumentDetails(documentId);
  }

  @DeleteMapping("/documents/{documentId}")
  public Mono<DeleteResponse> deleteDocument(@PathVariable int documentId) {
    return fastApiClient.deleteDocument(documentId);
  }

  @DeleteMapping("/clear-all")
  public Mono<DeleteResponse> clearAllDocuments() {
    return fastApiClient.clearAllDocuments();
  }
}