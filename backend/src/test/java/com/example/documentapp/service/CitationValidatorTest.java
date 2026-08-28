package com.example.documentapp.service;

import com.example.documentapp.dto.VerifyRequest;
import com.example.documentapp.dto.VerifyResponse;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class CitationValidatorTest {

  private CitationValidator validator;

  @BeforeEach
  void setUp() {
    validator = new CitationValidator();
  }

  @Test
  void extract_returnsEmptyList_whenAnswerIsNull() {
    List<Citation> citations = validator.extract(null);
    assertThat(citations).isEmpty();
  }

  @Test
  void extract_returnsEmptyList_whenAnswerIsBlank() {
    List<Citation> citations = validator.extract("");
    assertThat(citations).isEmpty();
  }

  @Test
  void extract_findsBracketCitations() {
    String answer = "The answer is here [doc1_p1_c1] and there (doc2_p2_c2).";
    List<Citation> citations = validator.extract(answer);

    assertThat(citations).hasSize(2);
    assertThat(citations.get(0).docId()).isEqualTo("doc1_p1_c1");
    assertThat(citations.get(1).docId()).isEqualTo("doc2_p2_c2");
  }

  @Test
  void extract_findsCurlyBraceCitations() {
    String answer = "See {doc3_p1_c3} for details.";
    List<Citation> citations = validator.extract(answer);

    assertThat(citations).hasSize(1);
    assertThat(citations.get(0).docId()).isEqualTo("doc3_p1_c3");
  }

  @Test
  void resolve_marksResolved_whenChunkMatches() {
    Citation citation = new Citation("doc1_p1_c1", 0, 0, "[doc1_p1_c1]");
    List<VerifyRequest.ChunkRef> chunks = List.of(
        new VerifyRequest.ChunkRef("doc1_p1_c1", 1, 1, "This is the doc1_p1_c1 content"));

    List<VerifyResponse.CitationCheck> results = validator.resolve(List.of(citation), chunks);

    assertThat(results).hasSize(1);
    assertThat(results.get(0).resolved()).isTrue();
    assertThat(results.get(0).status()).isEqualTo("SUPPORTED");
  }

  @Test
  void resolve_marksUnresolved_whenNoMatchingChunk() {
    Citation citation = new Citation("doc1_p1_c1", 0, 0, "[doc1_p1_c1]");
    List<VerifyRequest.ChunkRef> chunks = List.of(
        new VerifyRequest.ChunkRef("doc2_p1_c1", 1, 1, "Different content"));

    List<VerifyResponse.CitationCheck> results = validator.resolve(List.of(citation), chunks);

    assertThat(results).hasSize(1);
    assertThat(results.get(0).resolved()).isFalse();
    assertThat(results.get(0).status()).isEqualTo("UNRESOLVED");
  }

  @Test
  void resolve_calculatesSupportScore() {
    Citation citation = new Citation("doc1_p1_c1", 0, 0, "important information");
    List<VerifyRequest.ChunkRef> chunks = List.of(
        new VerifyRequest.ChunkRef("doc1_p1_c1", 1, 1, "This document contains important information"));

    List<VerifyResponse.CitationCheck> results = validator.resolve(List.of(citation), chunks);

    assertThat(results).hasSize(1);
    assertThat(results.get(0).supportScore()).isGreaterThan(0.0);
  }
}