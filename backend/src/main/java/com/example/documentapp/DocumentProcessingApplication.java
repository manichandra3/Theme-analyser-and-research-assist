package com.example.documentapp;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import com.example.documentapp.config.AppProperties;

@SpringBootApplication
@EnableConfigurationProperties(AppProperties.class)
public class DocumentProcessingApplication {
  public static void main(String[] args) {
    SpringApplication.run(DocumentProcessingApplication.class, args);
  }
}
