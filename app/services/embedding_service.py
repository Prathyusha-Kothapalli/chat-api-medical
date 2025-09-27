import logging
from typing import List, Dict, Any
import chromadb
from sentence_transformers import SentenceTransformer
from app.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        try:
            self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
            self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
            self.collection = self.client.get_or_create_collection(settings.COLLECTION_NAME)
            logger.info("✅ Embedding service initialized successfully")
        except Exception as e:
            logger.error(f"❌ Error initializing embedding service: {e}")
            raise

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        try:
            embeddings = self.embedding_model.encode(texts).tolist()
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    def store_document_chunks(self, document_id: str, chunks: List[Dict[str, Any]]):
        """Store document chunks in vector database"""
        try:
            texts = [chunk['text'] for chunk in chunks]
            embeddings = self.generate_embeddings(texts)
            metadatas = [
                {
                    'document_id': document_id,
                    'chunk_id': chunk['chunk_id'],
                    'start_index': chunk['start_index'],
                    'end_index': chunk['end_index']
                }
                for chunk in chunks
            ]
            ids = [f"{document_id}_{chunk['chunk_id']}" for chunk in chunks]
            
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Stored {len(chunks)} chunks for document {document_id}")
        except Exception as e:
            logger.error(f"Error storing document chunks: {str(e)}")
            raise
    
    def search_similar_chunks(self, query: str, n_results: int = 5, document_ids: List[str] = None) -> List[Dict[str, Any]]:
        """Search for similar chunks using semantic similarity"""
        try:
            query_embedding = self.generate_embeddings([query])[0]
            
            where = None
            if document_ids:
                where = {"document_id": {"$in": document_ids}}
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where
            )
            
            similar_chunks = []
            for i in range(len(results['documents'][0])):
                chunk_data = {
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if results['distances'] else None
                }
                similar_chunks.append(chunk_data)
            
            return similar_chunks
        except Exception as e:
            logger.error(f"Error searching similar chunks: {str(e)}")
            raise
    
    def delete_document_chunks(self, document_id: str):
        """Delete all chunks for a specific document from ChromaDB"""
        try:
            # Get all chunks for this document
            results = self.collection.get(where={"document_id": document_id})
            
            if results['ids']:
                # Delete chunks by their IDs
                self.collection.delete(ids=results['ids'])
                logger.info(f"Deleted {len(results['ids'])} chunks for document {document_id}")
            else:
                logger.info(f"No chunks found for document {document_id}")
                
        except Exception as e:
            logger.error(f"Error deleting document chunks for {document_id}: {str(e)}")
            raise

# Create a single instance
embedding_service = EmbeddingService()