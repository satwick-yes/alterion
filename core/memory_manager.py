import os
import json
import uuid
from pathlib import Path

class MemoryManager:
    def __init__(self):
        # Determine base directory
        import sys
        if getattr(sys, "frozen", False):
            base_dir = Path(sys.executable).parent
        else:
            base_dir = Path(__file__).resolve().parent.parent

        self.memory_file = base_dir / "config" / "memory.json"
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not self.memory_file.parent.exists():
            self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.memory_file.exists():
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump({"memories": []}, f, indent=4)

    def _load_memories(self) -> list:
        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("memories", [])
        except Exception:
            return []

    def _save_memories(self, memories: list):
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump({"memories": memories}, f, indent=4)

    def store_memory(self, fact: str) -> str:
        memories = self._load_memories()
        
        # Check for duplicates
        for mem in memories:
            if mem.get("fact", "").lower() == fact.lower():
                return "Fact already remembered."
                
        memories.append({
            "id": str(uuid.uuid4())[:8],
            "fact": fact
        })
        self._save_memories(memories)
        print(f"[MemoryManager] 🧠 Learned: {fact}")
        return f"Successfully remembered: {fact}"

    def search_memory(self, query: str) -> str:
        """
        Simple keyword-based extraction for now.
        For a production system, this could use embeddings/vector search.
        """
        memories = self._load_memories()
        if not memories:
            return ""

        # Extract words from query (ignore small words)
        ignore_words = {"the", "a", "an", "is", "my", "i", "to", "for", "with", "on", "in", "what", "how", "who", "where", "why"}
        query_words = [w.lower() for w in query.split() if w.lower() not in ignore_words and len(w) > 2]
        
        relevant = []
        for mem in memories:
            fact = mem.get("fact", "")
            fact_lower = fact.lower()
            # Score match based on word intersection
            score = sum(1 for w in query_words if w in fact_lower)
            
            # Or if it's a very broad query, just include all memories if memory bank is small (<10 items)
            if score > 0 or len(memories) < 20:
                relevant.append(fact)

        if not relevant:
            return ""
            
        return "USER MEMORIES/PREFERENCES:\n" + "\n".join(f"- {f}" for f in set(relevant))

memory_manager = MemoryManager()
