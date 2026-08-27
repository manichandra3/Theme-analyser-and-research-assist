package com.example.documentapp.dto;

import java.util.List;

public record GenerationEvalRequest(
    List<GenerationTestCase> testCases,
    int finalK
) {}