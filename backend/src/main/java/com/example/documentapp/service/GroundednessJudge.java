package com.example.documentapp.service;

import com.example.documentapp.dto.VerifyRequest.ChunkRef;

interface GroundednessJudge {

  double score(String answer, java.util.List<ChunkRef> chunks);
}