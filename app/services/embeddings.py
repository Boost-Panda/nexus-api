from sentence_transformers import SentenceTransformer
import faiss
from typing import List, Dict, Tuple
from app.services.storage import store_metadata, get_documents_by_vector_ids
from fastapi import UploadFile
import chardet
from datetime import datetime
import numpy as np
import os

model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.IndexFlatL2(384)  # Create a persistent index

# Constants
FAISS_INDEX_PATH = "faiss_index.bin"
VECTOR_DIM = 384

# Initialize or load FAISS index
def init_faiss_index():
    global index
    if os.path.exists(FAISS_INDEX_PATH):
        try:
            index = faiss.read_index(FAISS_INDEX_PATH)
            print(f"Loaded FAISS index with {index.ntotal} vectors")
        except Exception as e:
            print(f"Error loading index: {e}")
            index = create_new_index()
    else:
        index = create_new_index()

def create_new_index():
    """Create a new FAISS index optimized for cosine similarity"""
    # Use IndexFlatIP (Inner Product) with normalized vectors for cosine similarity
    index = faiss.IndexFlatIP(VECTOR_DIM)
    print("Created new FAISS index")
    return index

def normalize_vector(vector: np.ndarray) -> np.ndarray:
    """Normalize vector for cosine similarity"""
    return vector / np.linalg.norm(vector)

async def extract_text(file: UploadFile, content: bytes) -> str:
    """Extract text from various file types"""
    if file.content_type == 'application/pdf':
        from pdfminer.high_level import extract_text_to_fp
        from pdfminer.layout import LAParams
        import io
        output = io.StringIO()
        with io.BytesIO(content) as fp:
            extract_text_to_fp(fp, output, laparams=LAParams())
        return output.getvalue()
    
    elif file.content_type in ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
        from docx import Document
        import io
        doc = Document(io.BytesIO(content))
        return " ".join([paragraph.text for paragraph in doc.paragraphs])
    
    else:
        # Default to treating as text
        encoding = detect_encoding(content)
        return content.decode(encoding)

def detect_encoding(content: bytes) -> str:
    """Detect content encoding"""
    detection = chardet.detect(content)
    return detection['encoding'] or 'utf-8'

async def process_and_store(file: UploadFile) -> Dict:
    """Process uploaded file and store its embeddings"""
    content = await file.read()
    
    # Extract text and handle different file types
    text = await extract_text(file, content)
    
    # Generate and normalize embedding
    embedding = model.encode(text, show_progress_bar=False)
    normalized_embedding = normalize_vector(embedding)
    
    # Store in FAISS
    index.add(normalized_embedding.reshape(1, -1))
    vector_id = index.ntotal - 1
    
    # Save updated index
    faiss.write_index(index, FAISS_INDEX_PATH)
    
    print(f"Stored document with vector_id: {vector_id}")
    
    # Store metadata and content
    metadata = {
        "title": file.filename,
        "vector_id": vector_id,
        "content_type": file.content_type,
        "encoding": detect_encoding(content),
        "text_length": len(text),
        "additional_metadata": {
            "file_size": len(content),
            "processed_at": datetime.utcnow().isoformat()
        }
    }
    
    doc_id = store_metadata(metadata, text)
    metadata["id"] = doc_id
    
    return metadata

def search(query: str, top_n: int = 5) -> List[Dict]:
    """Search for similar documents with content"""
    try:
        # Generate and normalize query embedding
        query_vector = model.encode(query, show_progress_bar=False)
        normalized_query = normalize_vector(query_vector)
        
        # Ensure we have documents in the index
        if index.ntotal == 0:
            print("No documents in index")
            return []
            
        # Search in FAISS
        scores, vector_ids = index.search(normalized_query.reshape(1, -1), min(top_n, index.ntotal))
        
        # Filter out negative IDs and low similarity scores
        valid_results = [(float(score), int(vid)) 
                        for score, vid in zip(scores[0], vector_ids[0])
                        if vid >= 0 and score > 0.3]  # Adjust threshold as needed
        
        if not valid_results:
            print("No results above similarity threshold")
            return []
            
        # Sort by similarity score
        valid_results.sort(reverse=True)
        scores, vector_ids = zip(*valid_results)
        
        print(f"Query: '{query}'")
        print(f"Found vector_ids: {vector_ids}")
        print(f"Similarity scores: {scores}")
        
        # Get documents
        documents = get_documents_by_vector_ids(list(vector_ids))
        print(f"Retrieved {len(documents)} documents")
        
        # Add similarity scores and relevant chunks
        results = []
        for doc, score in zip(documents, scores):
            if doc.get("content"):
                doc["similarity_score"] = score
                doc["relevant_chunk"] = extract_relevant_chunk(doc["content"], query)
                results.append(doc)
        
        return results
        
    except Exception as e:
        print(f"Search error: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def extract_relevant_chunk(content: str, query: str, chunk_size: int = 500, context_size: int = 100) -> str:
    """Extract relevant chunk of text around query terms with context"""
    # Normalize text and query
    content_lower = content.lower()
    query_terms = set(query.lower().split())
    
    # Split into sentences (rough approximation)
    sentences = content.replace(".", ". ").replace("!", "! ").replace("?", "? ").split(". ")
    
    # Score each sentence based on query term matches
    sentence_scores = []
    for i, sentence in enumerate(sentences):
        score = sum(1 for term in query_terms if term in sentence.lower())
        if score > 0:
            sentence_scores.append((i, score))
    
    if not sentence_scores:
        # If no matches, return first chunk
        return content[:chunk_size]
    
    # Find best matching sentence
    best_sentence_idx = max(sentence_scores, key=lambda x: x[1])[0]
    
    # Get context around best matching sentence
    start_idx = max(0, best_sentence_idx - context_size)
    end_idx = min(len(sentences), best_sentence_idx + context_size + 1)
    
    relevant_sentences = sentences[start_idx:end_idx]
    return " ".join(relevant_sentences)

# Initialize index when module is loaded
init_faiss_index()
