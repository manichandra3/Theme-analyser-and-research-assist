package com.example.documentapp.dto;

import java.util.List;

public record RetrievalTestCase(
    String question,
    List<String> relevantChunkIds
) {}