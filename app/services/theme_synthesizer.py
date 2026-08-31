from typing import List, Dict, Any
import google.generativeai as genai
from core.config import settings

# Initialize Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

def generate_theme_prompt(answers: List[Dict[str, str]]) -> str:
    """Generate a prompt for the LLM to identify themes from document answers."""
    # Format answers for the prompt
    formatted_answers = "\n\n".join([
        f"Document {answer['doc_id']} (Page {answer['page']}, Paragraph {answer['paragraph']}):\n{answer['content']}"
        for answer in answers
        if answer['doc_id'] != 'Answer'  # Exclude the main answer
    ])
    
    return f"""Based on the following document answers, identify the main themes and provide a synthesized summary for each theme. 
Include specific citations for each theme using the format [Doc ID: X, Page: Y, Paragraph: Z].

Document Answers:
{formatted_answers}

Please provide your analysis in the following format:

Theme 1: [Theme Name]
Summary: [Brief description of the theme]
Supported by: [List of citations in format [Doc ID: X, Page: Y, Paragraph: Z]]

Theme 2: [Theme Name]
Summary: [Brief description of the theme]
Supported by: [List of citations in format [Doc ID: X, Page: Y, Paragraph: Z]]

[Continue for additional themes if present]

Analysis:"""

def format_themes_for_table(themes_text: str) -> List[Dict[str, str]]:
    """Format the LLM's theme analysis into a table-like structure."""
    table_rows = []
    
    # Split into themes
    theme_sections = themes_text.split("\n\n")
    
    for section in theme_sections:
        if not section.strip():
            continue
            
        lines = section.strip().split("\n")
        if not lines:
            continue
            
        # Extract theme name
        theme_name = lines[0].replace("Theme ", "").strip()
        
        # Extract summary
        summary = ""
        citations = []
        for line in lines[1:]:
            if line.startswith("Summary:"):
                summary = line.replace("Summary:", "").strip()
            elif line.startswith("Supported by:"):
                citations_text = line.replace("Supported by:", "").strip()
                # Parse citations
                citations = [
                    citation.strip("[]").split(", ")
                    for citation in citations_text.split("]")
                    if citation.strip()
                ]
        
        # Add theme row
        table_rows.append({
            "doc_id": f"Theme {theme_name}",
            "content": summary,
            "page": "",
            "paragraph": ""
        })
        
        # Add citation rows
        for citation in citations:
            if len(citation) >= 3:
                doc_id = citation[0].replace("Doc ID: ", "")
                page = citation[1].replace("Page: ", "")
                paragraph = citation[2].replace("Paragraph: ", "")
                
                table_rows.append({
                    "doc_id": doc_id,
                    "content": "Supporting evidence",
                    "page": page,
                    "paragraph": paragraph
                })
    
    return table_rows

async def synthesize_themes(answers: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Synthesize themes from document answers using LLM.
    
    Args:
        answers: List of document answers with citations
    
    Returns:
        List of dictionaries containing themes and their supporting citations
    """
    if not answers:
        return [{
            "doc_id": "Theme Analysis",
            "content": "No document answers available for theme analysis.",
            "page": "",
            "paragraph": ""
        }]
    
    # Generate prompt
    prompt = generate_theme_prompt(answers)
    
    # Get theme analysis from LLM
    response = model.generate_content(prompt)
    themes_text = response.text
    
    # Format themes into table structure
    return format_themes_for_table(themes_text) 
