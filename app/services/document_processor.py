import os
import pytesseract
from pdf2image import convert_from_path
import pdfplumber
from PIL import Image
from typing import List, Dict, Any
import json
from datetime import datetime
from core.config import settings
from db.models import Document, Page, Paragraph
from sqlalchemy.orm import Session
from .vector_store import store_document_chunks, split_text_into_chunks

class DocumentProcessor:
    def __init__(self, db: Session):
        self.db = db
        if settings.TESSERACT_CMD:
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

    async def process_document(self, file_path: str, filename: str) -> Document:
        """Process a document and extract text using OCR if needed."""
        file_type = self._get_file_type(filename)
        
        # Create document record
        document = Document(
            filename=filename,
            file_type=file_type,
            original_path=file_path,
            processed_path=str(settings.PROCESSED_DIR / f"{filename}.json")
        )
        self.db.add(document)
        self.db.commit()
        
        # Process based on file type
        if file_type == 'pdf':
            pages = self._process_pdf(file_path)
        elif file_type in ['jpg', 'jpeg', 'png']:
            pages = self._process_image(file_path)
        else:
            pages = self._process_text(file_path)
        
        # Save pages and paragraphs
        for page_num, page_content in enumerate(pages, 1):
            page = Page(
                document_id=document.id,
                page_number=page_num,
                content=page_content
            )
            self.db.add(page)
            self.db.commit()
            
            # Split into paragraphs and save
            paragraphs = page_content.split('\n\n')
            for para_num, para_content in enumerate(paragraphs, 1):
                if para_content.strip():
                    paragraph = Paragraph(
                        page_id=page.id,
                        paragraph_number=para_num,
                        content=para_content.strip()
                    )
                    self.db.add(paragraph)
            
            # Store in vector database
            chunks = split_text_into_chunks(page_content)
            store_document_chunks(str(document.id), page_num, chunks)
            
        self.db.commit()
        
        # Save processed data to JSON
        self._save_to_json(document)
        
        return document

    def _get_file_type(self, filename: str) -> str:
        """Get file type from filename."""
        return filename.split('.')[-1].lower()

    def _process_pdf(self, file_path: str) -> List[str]:
        """Process PDF file and extract text."""
        pages = []
        try:
            # First try to extract text directly
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        pages.append(text)
                    else:
                        # If no text found, use OCR
                        images = convert_from_path(file_path, first_page=page.page_number, last_page=page.page_number)
                        for image in images:
                            text = pytesseract.image_to_string(image)
                            pages.append(text)
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")
        return pages

    def _process_image(self, file_path: str) -> List[str]:
        """Process image file using OCR."""
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return [text]
        except Exception as e:
            raise Exception(f"Error processing image: {str(e)}")

    def _process_text(self, file_path: str) -> List[str]:
        """Process text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            return [text]
        except Exception as e:
            raise Exception(f"Error processing text file: {str(e)}")

    def _save_to_json(self, document: Document) -> None:
        """Save processed document data to JSON file."""
        data = {
            "document_id": document.id,
            "filename": document.filename,
            "file_type": document.file_type,
            "created_at": document.created_at.isoformat(),
            "pages": []
        }
        
        for page in document.pages:
            page_data = {
                "page_number": page.page_number,
                "content": page.content,
                "paragraphs": [
                    {
                        "paragraph_number": p.paragraph_number,
                        "content": p.content
                    }
                    for p in page.paragraphs
                ]
            }
            data["pages"].append(page_data)
        
        with open(document.processed_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2) 
