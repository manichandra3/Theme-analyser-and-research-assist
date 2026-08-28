package com.example.documentapp.service;

import com.example.documentapp.config.AppProperties;
import com.example.documentapp.dto.VerifyResponse;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class DefaultVerificationPolicyTest {

  @Mock
  private AppProperties properties;

  private DefaultVerificationPolicy policy;

  @BeforeEach
  void setUp() {
    when(properties.groundednessThreshold()).thenReturn(0.6);
    policy = new DefaultVerificationPolicy(properties);
  }

  @Test
  void determineVerdict_returnsPass_whenScoreAboveThresholdAndCitationsResolved() {
    List<VerifyResponse.CitationCheck> citations = List.of(
        new VerifyResponse.CitationCheck("[doc1]", true, 0.8, "SUPPORTED")
    );

    String verdict = policy.determineVerdict(0.85, citations);

    assertThat(verdict).isEqualTo("PASS");
  }

  @Test
  void determineVerdict_returnsLowGroundedness_whenScoreBelowThreshold() {
    List<VerifyResponse.CitationCheck> citations = List.of(
        new VerifyResponse.CitationCheck("[doc1]", true, 0.8, "SUPPORTED")
    );

    String verdict = policy.determineVerdict(0.4, citations);

    assertThat(verdict).isEqualTo("LOW_GROUNDEDNESS");
  }

  @Test
  void determineVerdict_returnsUnresolvedCitations_whenCitationsUnresolved() {
    List<VerifyResponse.CitationCheck> citations = List.of(
        new VerifyResponse.CitationCheck("[doc1]", false, 0.0, "UNRESOLVED")
    );

    String verdict = policy.determineVerdict(0.85, citations);

    assertThat(verdict).isEqualTo("UNRESOLVED_CITATIONS");
  }

  @Test
  void determineVerdict_returnsFail_whenBothFail() {
    List<VerifyResponse.CitationCheck> citations = List.of(
        new VerifyResponse.CitationCheck("[doc1]", false, 0.0, "UNRESOLVED")
    );

    String verdict = policy.determineVerdict(0.4, citations);

    assertThat(verdict).isEqualTo("FAIL");
  }

  @Test
  void collectIssues_includesGroundednessIssue_whenBelowThreshold() {
    List<VerifyResponse.CitationCheck> citations = List.of(
        new VerifyResponse.CitationCheck("[doc1]", true, 0.8, "SUPPORTED")
    );

    List<String> issues = policy.collectIssues(0.4, citations);

    assertThat(issues).contains("Groundedness score 0.40 below threshold 0.60");
  }

  @Test
  void collectIssues_includesUnresolvedCount_whenCitationsUnresolved() {
    List<VerifyResponse.CitationCheck> citations = List.of(
        new VerifyResponse.CitationCheck("[doc1]", false, 0.0, "UNRESOLVED"),
        new VerifyResponse.CitationCheck("[doc2]", false, 0.0, "UNRESOLVED")
    );

    List<String> issues = policy.collectIssues(0.85, citations);

    assertThat(issues).contains("2 unresolved citation(s)");
  }

  @Test
  void collectIssues_includesWeakSupport_whenSupportScoreLow() {
    List<VerifyResponse.CitationCheck> citations = List.of(
        new VerifyResponse.CitationCheck("[doc1]", true, 0.3, "WEAK_SUPPORT")
    );

    List<String> issues = policy.collectIssues(0.85, citations);

    assertThat(issues).contains("Weak support for citation '[doc1]': 0.30");
  }
}