package com.example.documentapp.dto;

import java.util.List;
import java.util.Map;

public record PerQuestionResult(
    String question,
    Map<String, Double> metrics,
    List<String> retrievedChunkIds
) {}