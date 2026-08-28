package com.example.documentapp.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.reactive.ReactorClientHttpConnector;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.netty.http.client.HttpClient;
import java.time.Duration;

@Configuration
public class WebClientConfig {

  @Bean
  public WebClient fastApiWebClient(AppProperties appProperties) {
    var fastApiProps = appProperties.fastapi();
    HttpClient httpClient = HttpClient.create()
        .responseTimeout(Duration.ofSeconds(fastApiProps.timeoutSeconds()))
        .compress(true);
    return WebClient.builder()
        .baseUrl(fastApiProps.baseUrl())
        .clientConnector(new ReactorClientHttpConnector(httpClient))
        .defaultHeader("Content-Type", "application/json")
        .build();
  }
}