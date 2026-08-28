package com.example.documentapp.service;

import com.example.documentapp.dto.VerifyRequest;
import com.example.documentapp.dto.VerifyResponse;
import org.springframework.stereotype.Component;

@Component
public class VerificationPipeline {

  private final CitationValidator citationValidator;
  private final GroundednessJudgeFactory judgeFactory;
  private final VerificationPolicy policy;

  public VerificationPipeline(CitationValidator citationValidator,
      GroundednessJudgeFactory judgeFactory,
      VerificationPolicy policy) {
    this.citationValidator = citationValidator;
    this.judgeFactory = judgeFactory;
    this.policy = policy;
  }

  public VerifyResponse execute(VerifyRequest request) {
    GroundednessJudge judge = judgeFactory.createJudge();

    var citations = citationValidator.extract(request.answer());
    var resolvedCitations = citationValidator.resolve(citations, request.chunks());
    double groundednessScore = judge.score(request.answer(), request.chunks());

    String verdict = policy.determineVerdict(groundednessScore, resolvedCitations);
    var issues = policy.collectIssues(groundednessScore, resolvedCitations);

    return new VerifyResponse(verdict, groundednessScore, resolvedCitations, issues);
  }
}