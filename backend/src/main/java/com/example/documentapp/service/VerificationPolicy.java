package com.example.documentapp.service;

import com.example.documentapp.dto.VerifyResponse;
import java.util.List;

public interface VerificationPolicy {

  String determineVerdict(double groundednessScore, List<VerifyResponse.CitationCheck> citations);

  List<String> collectIssues(double groundednessScore, List<VerifyResponse.CitationCheck> citations);
}