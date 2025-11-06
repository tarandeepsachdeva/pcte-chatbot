import PyPDF2
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os
from typing import List, Tuple

class PDFProcessor:
    def __init__(self, pdf_path: str):
        """Initialize the PDF processor with the path to the PCTE brochure PDF."""
        self.pdf_path = pdf_path
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.text_chunks = []
        self.embeddings = None
        
    def load_and_chunk_pdf(self, chunk_size: int = 500) -> None:
        """Load PDF and split into chunks."""
        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(f"PDF file not found at {self.pdf_path}")
        
        text = ""
        with open(self.pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        
        # Simple text chunking
        self.text_chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
    def generate_embeddings(self) -> None:
        """Generate embeddings for all text chunks."""
        if not self.text_chunks:
            self.load_and_chunk_pdf()
        self.embeddings = self.model.encode(self.text_chunks)
    
    def find_relevant_chunks(self, query: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """Find the most relevant text chunks for a given query."""
        if self.embeddings is None:
            self.generate_embeddings()
            
        query_embedding = self.model.encode([query])
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        return [(self.text_chunks[i], float(similarities[i])) for i in top_indices]
    
    def get_context_for_query(self, query: str, top_k: int = 3) -> str:
        """Get formatted context for a query."""
        relevant_chunks = self.find_relevant_chunks(query, top_k)
        context_parts = []
        
        for i, (chunk, score) in enumerate(relevant_chunks, 1):
            context_parts.append(f"--- Relevant Information {i} (Relevance: {score:.2f}) ---\n{chunk}")
            
        return "\n\n".join(context_parts)

# Initialize the PDF processor (will be used as a singleton)
pdf_processor = None

def get_pdf_processor():
    """Get or create the PDF processor instance."""
    global pdf_processor
    if pdf_processor is None:
        pdf_path = os.path.join(os.path.dirname(__file__), 'pcte_brochure.pdf')
        pdf_processor = PDFProcessor(pdf_path)
        try:
            pdf_processor.load_and_chunk_pdf()
            pdf_processor.generate_embeddings()
            print("PDF processor initialized successfully")
        except Exception as e:
            print(f"Error initializing PDF processor: {str(e)}")
    return pdf_processor
