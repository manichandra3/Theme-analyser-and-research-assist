package com.example.documentapp.dto;

import java.util.Map;

public record SearchResult(
    String text,
    Map<String, Object> metadata,
    Double denseScore,
    Double sparseScore,
    Double hybridScore,
    java.util.List<String> sources
) {}