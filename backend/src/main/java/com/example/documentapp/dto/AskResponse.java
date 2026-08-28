package com.example.documentapp.dto;

import java.util.List;

public record AskResponse(
    List<AskItem> items
) {}