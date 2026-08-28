package com.example.documentapp.service;

import com.example.documentapp.dto.VerifyRequest;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

@ExtendWith(MockitoExtension.class)
class LexicalGroundednessJudgeTest {

  private LexicalGroundednessJudge judge;

  @BeforeEach
  void setUp() {
    judge = new LexicalGroundednessJudge();
  }

  @Test
  void score_returnsZero_whenAnswerIsNull() {
    double score = judge.score(null, List.of());
    assertThat(score).isEqualTo(0.0);
  }

  @Test
  void score_returnsZero_whenAnswerIsBlank() {
    double score = judge.score("", List.of());
    assertThat(score).isEqualTo(0.0);
  }

  @Test
  void score_returnsZero_whenChunksEmpty() {
    double score = judge.score("some answer", List.of());
    assertThat(score).isEqualTo(0.0);
  }

  @Test
  void score_returnsHigh_whenAnswerMatchesChunks() {
    List<VerifyRequest.ChunkRef> chunks = List.of(
        new VerifyRequest.ChunkRef("doc1", 1, 1, "The system uses machine learning for classification"),
        new VerifyRequest.ChunkRef("doc2", 2, 1, "Neural networks are a type of machine learning model")
    );

    String answer = "Machine learning and neural networks are used for classification";
    double score = judge.score(answer, chunks);

    assertThat(score).isGreaterThan(0.3);
    assertThat(score).isLessThanOrEqualTo(1.0);
  }

  @Test
  void score_returnsLow_whenAnswerUnrelated() {
    List<VerifyRequest.ChunkRef> chunks = List.of(
        new VerifyRequest.ChunkRef("doc1", 1, 1, "The system uses machine learning for classification")
    );

    String answer = "The weather today is sunny and warm";
    double score = judge.score(answer, chunks);

    assertThat(score).isLessThan(0.3);
  }

  @Test
  void supportScore_returnsHigh_whenClaimSupported() {
    VerifyRequest.ChunkRef chunk = new VerifyRequest.ChunkRef(
        "doc1", 1, 1, "Machine learning algorithms classify data effectively");
    String claim = "Machine learning classifies data";

    double score = judge.supportScore(claim, chunk);

    assertThat(score).isGreaterThan(0.5);
  }

  @Test
  void supportScore_returnsZero_whenClaimUnsupported() {
    VerifyRequest.ChunkRef chunk = new VerifyRequest.ChunkRef(
        "doc1", 1, 1, "Machine learning algorithms classify data effectively");
    String claim = "Weather forecasting uses satellites";

    double score = judge.supportScore(claim, chunk);

    assertThat(score).isEqualTo(0.0);
  }
}