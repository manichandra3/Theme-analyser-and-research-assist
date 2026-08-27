package com.example.documentapp.dto;

public record GenerationResult(
    String question,
    String answer,
    GenerationMetrics metrics
) {}