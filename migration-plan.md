Browser --> Spring Boot (port 8000) --HTTP--> Python RAG service (port 8001)
                                               rag/, Chroma, Gemini, OCR 

Spring Boot --> public api, H2 metadata DB, file storage, CORS, and error handling.

Python --> everything under app/rag/ (chunking, hybrid retrieval, BM25, rewriting, HyDE, reranking, generation, judges, metrics) plus vector store, document_processor, theme_synthesizer, and evaluation_service.

backend/
  pom.xml 
  Dockerfile
  src/main/
    java/com/example/doucmentapp/
      DocumentProcessingApplication.java
      config/
        AppProperties.java
        RagClientConfig.java
      controller/
        DocumentController, SearchController, QaController, etc...
        dto/
        entity/
        repository/
        service/
        web/
    resources/application.yml 


option A: Spring Boot api + Python RAG engine 
option B: Full Spring AI in java 

Spring AI support 
1. Gemini chat 
2. Gemini embeddings
3. Chroma vector store
4. PDF/OCR reader
5. Basic RAG flow

Not supported by SpringAI 
Query rewriting + HyDE 
Hybrid dnese+BM25 with RRF fusion - chroma SpringAI is dense only 
LLM reranking 
LLm-as-judge + retrieval metrics 
Theme synthesis 

-------------------------------------------------
                      OR
-------------------------------------------------


Make the SpringBoot application an optional middleware to valdiate RAG modle outputs 
essentially a post processing gateway 

User -> question -> RAG -> ouput -> middleware -valid-> User 
                                       |
                     ^                 |
                     |---------------invalid
                        
