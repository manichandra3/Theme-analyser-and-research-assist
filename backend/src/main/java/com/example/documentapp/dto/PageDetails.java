package com.example.documentapp.dto;

import java.util.List;

public record PageDetails(
    int pageNumber,
    String content,
    List<ParagraphDetails> paragraphs
) {}