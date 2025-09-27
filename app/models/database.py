from typing import Dict, List, Any, Optional
from datetime import datetime
import chromadb
from chromadb.config import Settings as ChromaSettings
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class VectorDatabase:
    def __init__(self):
        # self.client = chromadb.PersistentClient(
        #     path=settings.CHROMA_DB_PATH,
        #     settings=ChromaSettings(anonymized_telemetry=False)
        # )
        self.client = chromadb.Client()

        self.collection = self.client.get_or_create_collection(
            name=settings.COLLECTION_NAME,
            metadata={"description": "Healthcare documents embedding store"}
        )
        logger.info(f"✅ Vector database initialized at {settings.CHROMA_DB_PATH}")
    
    def add_documents(self, documents: List[str], metadatas: List[Dict], ids: List[str]):
        """Add documents to the vector database"""
        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"✅ Added {len(documents)} documents to vector database")
        except Exception as e:
            logger.error(f"❌ Error adding documents to vector database: {e}")
            raise
    
    def search(self, query: str, n_results: int = 5, document_ids: Optional[List[str]] = None) -> List[Dict]:
        """Search for similar documents"""
        try:
            logger.info(f"🔍 Searching for: '{query}' (n_results: {n_results})")
            
            if document_ids:
                logger.info(f"🔍 Filtering by document IDs: {document_ids}")
                results = self.collection.query(
                    query_texts=[query],
                    n_results=n_results,
                    where={"document_id": {"$in": document_ids}}
                )
            else:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=n_results
                )
            
            formatted_results = self._format_search_results(results)
            logger.info(f"🔍 Found {len(formatted_results)} results")
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Error searching vector database: {e}")
            return []
    
    def _format_search_results(self, results) -> List[Dict]:
        """Format search results into a structured format"""
        formatted_results = []
        
        if results and results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    'document': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else None,
                    'id': results['ids'][0][i] if results['ids'] else None
                })
                logger.info(f"📄 Result {i+1}: {doc[:100]}...")
        
        return formatted_results
    
    def delete_documents(self, document_id: str):
        """Delete all chunks for a specific document"""
        try:
            self.collection.delete(where={"document_id": document_id})
            logger.info(f"✅ Deleted documents for ID: {document_id}")
        except Exception as e:
            logger.error(f"❌ Error deleting documents: {e}")
            raise

# Global vector database instance
vector_db = VectorDatabase()