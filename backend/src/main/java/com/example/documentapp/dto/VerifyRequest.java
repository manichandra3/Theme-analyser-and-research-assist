package com.example.documentapp.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import java.util.List;

public record VerifyRequest(
    @NotBlank String question,
    @NotBlank String answer,
    @NotEmpty List<ChunkRef> chunks) {

  public record ChunkRef(
      String docId,
      int page,
      int paragraph,
      String content) {
  }
}