package com.example.documentapp.dto;

import java.util.List;

public record DocumentDetails(
    int id,
    String filename,
    String fileType,
    String createdAt,
    List<PageDetails> pages
) {}