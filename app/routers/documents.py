from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import os
import aiofiles
from datetime import datetime
import shutil

from db.database import get_db
from services.document_processor import DocumentProcessor
from core.config import settings
from services.vector_store import collection

router = APIRouter()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process a document."""
    # Validate file type
    allowed_types = ['pdf', 'jpg', 'jpeg', 'png', 'txt']
    file_type = file.filename.split('.')[-1].lower()
    if file_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed_types)}"
        )
    
    # Create unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = settings.UPLOAD_DIR / filename
    
    # Save uploaded file
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error saving file: {str(e)}"
        )
    
    # Process document
    try:
        processor = DocumentProcessor(db)
        document = await processor.process_document(str(file_path), filename)
        return {
            "message": "Document processed successfully",
            "document_id": document.id,
            "filename": document.filename
        }
    except Exception as e:
        # Clean up file if processing fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )

@router.get("/documents")
async def list_documents(db: Session = Depends(get_db)):
    """List all processed documents."""
    from ..db.models import Document
    documents = db.query(Document).all()
    return [
        {
            "id": doc.id,
            "filename": doc.filename,
            "file_type": doc.file_type,
            "created_at": doc.created_at.isoformat()
        }
        for doc in documents
    ]

@router.get("/documents/{document_id}")
async def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get document details and content."""
    from ..db.models import Document
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "id": document.id,
        "filename": document.filename,
        "file_type": document.file_type,
        "created_at": document.created_at.isoformat(),
        "pages": [
            {
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
            for page in document.pages
        ]
    }

@router.delete("/clear-all")
async def clear_all_documents(db: Session = Depends(get_db)):
    """
    Clear all documents from the database, vector store, and file system.
    This will delete:
    - All document records from the database
    - All vectors from the vector store
    - All files from the upload and processed directories
    """
    try:
        # Clear vector store
        collection.delete(
            where={"$and": [{"doc_id": {"$exists": True}}]}
        )
        
        # Clear database
        from ..db.models import Document, Page, Paragraph
        db.query(Paragraph).delete()
        db.query(Page).delete()
        db.query(Document).delete()
        db.commit()
        
        # Clear file system
        if os.path.exists(settings.UPLOAD_DIR):
            shutil.rmtree(settings.UPLOAD_DIR)
            os.makedirs(settings.UPLOAD_DIR)
            
        if os.path.exists(settings.PROCESSED_DIR):
            shutil.rmtree(settings.PROCESSED_DIR)
            os.makedirs(settings.PROCESSED_DIR)
        
        return {"message": "All documents cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{document_id}")
async def delete_document(document_id: int, db: Session = Depends(get_db)):
    """
    Delete a specific document from the database, vector store, and file system.
    """
    from ..db.models import Document, Page, Paragraph
    
    # Get document
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        # Delete from vector store
        collection.delete(
            where={"doc_id": str(document_id)}
        )
        
        # Delete from database
        db.query(Paragraph).filter(Paragraph.page_id.in_(
            db.query(Page.id).filter(Page.document_id == document_id)
        )).delete(synchronize_session=False)
        db.query(Page).filter(Page.document_id == document_id).delete()
        db.query(Document).filter(Document.id == document_id).delete()
        db.commit()
        
        # Delete files
        file_path = settings.UPLOAD_DIR / document.filename
        if os.path.exists(file_path):
            os.remove(file_path)
            
        processed_dir = settings.PROCESSED_DIR / str(document_id)
        if os.path.exists(processed_dir):
            shutil.rmtree(processed_dir)
        
        return {"message": f"Document {document_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
