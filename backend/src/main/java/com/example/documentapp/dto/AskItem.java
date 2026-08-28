package com.example.documentapp.dto;

public record AskItem(
    String docId,
    String content,
    String page,
    String paragraph
) {}