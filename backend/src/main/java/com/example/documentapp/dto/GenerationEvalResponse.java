package com.example.documentapp.dto;

import java.util.List;

public record GenerationEvalResponse(
    List<GenerationResult> results
) {}