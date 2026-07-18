import json
import logging
import time
import sys
import threading
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
from core.inference_wrapper import inference_client

logger = logging.getLogger("vector_memory")

def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = get_base_dir()
VECTOR_DB_PATH = BASE_DIR / "memory" / "vector_db.json"
_lock = threading.Lock()

class VectorMemoryDB:
    def __init__(self):
        self.db = []
        self._load_db()

    def _load_db(self):
        with _lock:
            try:
                if VECTOR_DB_PATH.exists():
                    with open(VECTOR_DB_PATH, "r", encoding="utf-8") as f:
                        self.db = json.load(f)
                    logger.info(f"[VectorMemory] Loaded {len(self.db)} memory vectors.")
            except Exception as e:
                logger.error(f"[VectorMemory] Failed to load vector database: {e}")
                self.db = []

    def _save_db(self):
        with _lock:
            try:
                VECTOR_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
                with open(VECTOR_DB_PATH, "w", encoding="utf-8") as f:
                    json.dump(self.db, f, indent=2, ensure_ascii=False)
            except Exception as e:
                logger.error(f"[VectorMemory] Failed to save vector database: {e}")

    def add_memory(self, text: str, category: str = "general"):
        if not text or len(text.strip()) < 5:
            return
        
        try:
            # Check if this exact text is already stored
            for item in self.db:
                if item.get("text") == text:
                    return
            
            logger.info(f"[VectorMemory] Embedding text: '{text[:40]}...'")
            embedding = inference_client.generate_embedding(text)
            
            new_item = {
                "text": text,
                "category": category,
                "embedding": embedding,
                "timestamp": time.time()
            }
            
            self.db.append(new_item)
            self._save_db()
            logger.info(f"[VectorMemory] Saved memory item to vector store.")
        except Exception as e:
            logger.error(f"[VectorMemory] Add memory failed: {e}")

    def search_memories(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        if not query or not self.db:
            return []
        
        try:
            logger.info(f"[VectorMemory] Searching memory for: '{query[:40]}...'")
            query_vector = np.array(inference_client.generate_embedding(query))
            
            results = []
            for item in self.db:
                stored_vector = np.array(item["embedding"])
                
                # Compute Cosine Similarity
                dot_product = np.dot(query_vector, stored_vector)
                norm_q = np.linalg.norm(query_vector)
                norm_s = np.linalg.norm(stored_vector)
                
                similarity = dot_product / (norm_q * norm_s) if norm_q > 0 and norm_s > 0 else 0.0
                results.append((similarity, item))
                
            # Sort by similarity descending
            results.sort(key=lambda x: x[0], reverse=True)
            
            # Filter matches above similarity threshold (e.g. 0.4)
            filtered = [item for sim, item in results[:limit] if sim > 0.4]
            logger.info(f"[VectorMemory] Found {len(filtered)} matching memory contexts.")
            return filtered
        except Exception as e:
            logger.error(f"[VectorMemory] Search failed: {e}")
            return []

    def format_search_results(self, matches: List[Dict[str, Any]]) -> str:
        if not matches:
            return ""
        
        lines = ["[HISTORICAL CONTEXT & RELEVANT PAST INTERACTIONS]"]
        for match in matches:
            lines.append(f"- ({match.get('category', 'general')}): {match.get('text')}")
        return "\n".join(lines) + "\n\n"

# Global database instance
vector_memory_db = VectorMemoryDB()
