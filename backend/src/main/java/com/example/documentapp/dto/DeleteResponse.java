package com.example.documentapp.dto;

public record DeleteResponse(
    boolean success,
    String message
) {}