package com.example.documentapp.dto;

public record DocumentUploadResponse(
    boolean success,
    String message,
    Integer documentId,
    String filename
) {}