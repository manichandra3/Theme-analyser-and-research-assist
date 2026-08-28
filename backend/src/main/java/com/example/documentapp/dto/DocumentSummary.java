package com.example.documentapp.dto;

public record DocumentSummary(
    int id,
    String filename,
    String fileType,
    String createdAt
) {}