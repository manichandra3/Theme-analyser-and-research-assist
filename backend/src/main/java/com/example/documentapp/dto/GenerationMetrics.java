package com.example.documentapp.dto;

public record GenerationMetrics(
    double faithfulness,
    double answerRelevance
) {}