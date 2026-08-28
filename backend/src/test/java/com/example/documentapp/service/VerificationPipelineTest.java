package com.example.documentapp.service;

import com.example.documentapp.config.AppProperties;
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
class VerificationPipelineTest {

  @Mock
  private CitationValidator citationValidator;

  @Mock
  private GroundednessJudgeFactory judgeFactory;

  @Mock
  private VerificationPolicy policy;

  @Mock
  private GroundednessJudge judge;

  private VerificationPipeline pipeline;

  @BeforeEach
  void setUp() {
    pipeline = new VerificationPipeline(citationValidator, judgeFactory, policy);
  }

  @Test
  void execute_returnsPass_whenAllChecksPass() {
    VerifyRequest request = new VerifyRequest(
        "What is ML?",
        "Machine learning is a subset of AI [doc1_p1_c1]",
        List.of(new VerifyRequest.ChunkRef("doc1_p1_c1", 1, 1, "Machine learning is a subset of AI"))
    );

    Citation citation = new Citation("doc1_p1_c1", 0, 0, "[doc1_p1_c1]");
    VerifyResponse.CitationCheck check = new VerifyResponse.CitationCheck(
        "[doc1_p1_c1]", true, 0.8, "SUPPORTED");

    when(judgeFactory.createJudge()).thenReturn(judge);
    when(judge.score(anyString(), anyList())).thenReturn(0.85);
    when(citationValidator.extract(anyString())).thenReturn(List.of(citation));
    when(citationValidator.resolve(anyList(), anyList())).thenReturn(List.of(check));
    when(policy.determineVerdict(eq(0.85), anyList())).thenReturn("PASS");
    when(policy.collectIssues(eq(0.85), anyList())).thenReturn(List.of());

    VerifyResponse response = pipeline.execute(request);

    assertThat(response.verdict()).isEqualTo("PASS");
    assertThat(response.groundednessScore()).isEqualTo(0.85);
    assertThat(response.citations()).hasSize(1);
    assertThat(response.issues()).isEmpty();
  }

  @Test
  void execute_returnsFail_whenGroundednessLow() {
    VerifyRequest request = new VerifyRequest(
        "What is ML?",
        "Machine learning is a subset of AI [doc1_p1_c1]",
        List.of(new VerifyRequest.ChunkRef("doc1_p1_c1", 1, 1, "Machine learning is a subset of AI"))
    );

    Citation citation = new Citation("doc1_p1_c1", 0, 0, "[doc1_p1_c1]");
    VerifyResponse.CitationCheck check = new VerifyResponse.CitationCheck(
        "[doc1_p1_c1]", true, 0.8, "SUPPORTED");

    when(judgeFactory.createJudge()).thenReturn(judge);
    when(judge.score(anyString(), anyList())).thenReturn(0.3);
    when(citationValidator.extract(anyString())).thenReturn(List.of(citation));
    when(citationValidator.resolve(anyList(), anyList())).thenReturn(List.of(check));
    when(policy.determineVerdict(eq(0.3), anyList())).thenReturn("LOW_GROUNDEDNESS");
    when(policy.collectIssues(eq(0.3), anyList())).thenReturn(List.of("Groundedness score 0.30 below threshold 0.60"));

    VerifyResponse response = pipeline.execute(request);

    assertThat(response.verdict()).isEqualTo("LOW_GROUNDEDNESS");
    assertThat(response.groundednessScore()).isEqualTo(0.3);
    assertThat(response.issues()).contains("Groundedness score 0.30 below threshold 0.60");
  }

  @Test
  void execute_returnsFail_whenCitationsUnresolved() {
    VerifyRequest request = new VerifyRequest(
        "What is ML?",
        "Machine learning is a subset of AI [doc1_p1_c1]",
        List.of(new VerifyRequest.ChunkRef("doc2_p1_c1", 1, 1, "Different content"))
    );

    Citation citation = new Citation("doc1_p1_c1", 0, 0, "[doc1_p1_c1]");
    VerifyResponse.CitationCheck check = new VerifyResponse.CitationCheck(
        "[doc1_p1_c1]", false, 0.0, "UNRESOLVED");

    when(judgeFactory.createJudge()).thenReturn(judge);
    when(judge.score(anyString(), anyList())).thenReturn(0.85);
    when(citationValidator.extract(anyString())).thenReturn(List.of(citation));
    when(citationValidator.resolve(anyList(), anyList())).thenReturn(List.of(check));
    when(policy.determineVerdict(eq(0.85), anyList())).thenReturn("UNRESOLVED_CITATIONS");
    when(policy.collectIssues(eq(0.85), anyList())).thenReturn(List.of("1 unresolved citation(s)"));

    VerifyResponse response = pipeline.execute(request);

    assertThat(response.verdict()).isEqualTo("UNRESOLVED_CITATIONS");
    assertThat(response.issues()).contains("1 unresolved citation(s)");
  }
}