package com.example.documentapp.dto;

import java.util.List;

public record RetrievalEvalRequest(
    List<RetrievalTestCase> testCases,
    int evalK
) {}