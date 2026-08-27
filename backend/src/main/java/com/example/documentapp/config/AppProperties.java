package com.example.documentapp.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "app")
public record AppProperties(
    String geminiApiKey,
    String geminiModel,
    double groundednessThreshold,
    FastApiProperties fastapi) {

  @ConfigurationProperties(prefix = "app.fastapi")
  public record FastApiProperties(
      String baseUrl,
      int timeoutSeconds) {
  }
}