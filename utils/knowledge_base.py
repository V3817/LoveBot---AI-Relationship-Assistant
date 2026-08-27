import chromadb
import os
from typing import List, Dict, Optional
import uuid
import PyPDF2
from io import BytesIO
from duckduckgo_search import DDGS

class KnowledgeBaseManager:
    def __init__(self):
        # Initialize ChromaDB client with persistent storage
        self.client = chromadb.PersistentClient(path="./knowledge_base")
        # Create or get the collection
        self.collection = self.client.get_or_create_collection(
            name="relationship_knowledge",
            metadata={"description": "Relationship advice and psychology knowledge"}
        )
        # Initialize DuckDuckGo search
        self.ddgs = DDGS()
    
    def add_document(self, text: str = None, file=None, metadata: Optional[Dict] = None) -> str:
        """
        Add a document to the knowledge base
        Args:
            text: Direct text content
            file: Streamlit UploadedFile object
            metadata: Additional metadata for the document
        Returns: document_id
        """
        doc_id = str(uuid.uuid4())
        if metadata is None:
            metadata = {}
        
        # Process file if provided
        if file is not None:
            if file.type == "application/pdf":
                text = self._extract_pdf_text(file)
                metadata["file_type"] = "pdf"
            else:
                text = file.read().decode()
                metadata["file_type"] = "text"
            metadata["filename"] = file.name
        
        if not text:
            raise ValueError("No content provided")
        
        # Split long documents into chunks
        chunks = self._chunk_text(text)
        
        # Add chunks to the collection
        for i, chunk in enumerate(chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata["chunk_index"] = i
            chunk_metadata["total_chunks"] = len(chunks)
            self.collection.add(
                documents=[chunk],
                metadatas=[chunk_metadata],
                ids=[f"{doc_id}_chunk_{i}"]
            )
        return doc_id
    
    def _extract_pdf_text(self, file) -> str:
        """Extract text content from PDF file"""
        try:
            pdf_content = BytesIO(file.read())
            reader = PyPDF2.PdfReader(pdf_content)
            text = []
            for page in reader.pages:
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
                except Exception as e:
                    print(f"Error extracting text from page: {e}")
                    continue
            return "\n".join(text)
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    
    def _chunk_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Split text into smaller chunks"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        for word in words:
            current_size += len(word) + 1  # +1 for space
            if current_size > chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_size = len(word)
            else:
                current_chunk.append(word)
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        return chunks
    
    def search_web(self, query: str, max_results: int = 3) -> List[Dict]:
        """Search the web using DuckDuckGo"""
        try:
            results = []
            for r in self.ddgs.text(query, max_results=max_results):
                results.append({
                    'title': r['title'],
                    'body': r['body'],
                    'link': r['link']
                })
            return results
        except Exception as e:
            print(f"Web search error: {e}")
            return []
    
    def enrich_knowledge_base(self, query: str):
        """Enrich knowledge base with web search results"""
        web_results = self.search_web(query)
        for result in web_results:
            try:
                self.add_document(
                    text=f"{result['title']}\n\n{result['body']}",
                    metadata={
                        "source": "web",
                        "url": result['link'],
                        "query": query
                    }
                )
            except Exception as e:
                print(f"Error adding web result to knowledge base: {e}")
    
    def get_relevant_context(self, query: str, include_web_search: bool = True) -> str:
        """Get relevant context for a query"""
        if include_web_search:
            try:
                self.enrich_knowledge_base(query)
            except Exception as e:
                print(f"Error enriching knowledge base: {e}")
        
        results = self.search_similar(query)
        if not results:
            return ""
        
        context = "Based on available knowledge:\n\n"
        for idx, doc in enumerate(results, 1):
            source = doc['metadata'].get('source', 'local')
            if source == 'web':
                context += f"{idx}. [Web Source] {doc['content']}\n\n"
            else:
                context += f"{idx}. {doc['content']}\n\n"
        return context.strip()
    
    def search_similar(self, query: str, n_results: int = 3) -> List[Dict]:
        """Search for similar content"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        # Format results
        documents = []
        for idx, doc in enumerate(results['documents'][0]):
            documents.append({
                'content': doc,
                'metadata': results['metadatas'][0][idx] if results['metadatas'] else {},
                'id': results['ids'][0][idx]
            })
        return documents
