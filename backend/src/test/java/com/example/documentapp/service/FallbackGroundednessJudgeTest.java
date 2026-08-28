package com.example.documentapp.service;

import com.example.documentapp.dto.VerifyRequest;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class FallbackGroundednessJudgeTest {

  @Mock
  private GroundednessJudge primary;

  @Mock
  private GroundednessJudge fallback;

  private FallbackGroundednessJudge judge;

  @BeforeEach
  void setUp() {
    judge = new FallbackGroundednessJudge(primary, fallback);
  }

  @Test
  void score_returnsPrimaryScore_whenPrimarySucceeds() {
    when(primary.score(anyString(), anyList())).thenReturn(0.75);

    double score = judge.score("answer", List.of());

    assertThat(score).isEqualTo(0.75);
    verify(fallback, never()).score(anyString(), anyList());
  }

  @Test
  void score_returnsFallbackScore_whenPrimaryFails() {
    when(primary.score(anyString(), anyList())).thenReturn(-1.0);
    when(fallback.score(anyString(), anyList())).thenReturn(0.65);

    double score = judge.score("answer", List.of());

    assertThat(score).isEqualTo(0.65);
  }

  @Test
  void score_returnsFallbackScore_whenPrimaryReturnsNegative() {
    when(primary.score(anyString(), anyList())).thenReturn(-0.5);
    when(fallback.score(anyString(), anyList())).thenReturn(0.45);

    double score = judge.score("answer", List.of());

    assertThat(score).isEqualTo(0.45);
  }
}