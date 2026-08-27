package com.example.documentapp.dto;

import java.util.List;
import java.util.Map;

public record RetrievalEvalResponse(
    Map<String, Double> averages,
    List<PerQuestionResult> perQuestion
) {}