from typing import List, Dict
from dataclasses import dataclass
from datetime import datetime
import numpy as np

@dataclass
class MemoryNode:
    content: str
    embedding: np.ndarray
    children: List['MemoryNode']
    summary: str = ""
    created_at: datetime = datetime.utcnow()
    
class MemoryWalker:
    def __init__(self, model, chunk_size=500):
        self.model = model
        self.chunk_size = chunk_size
        
    def build_memory_tree(self, document: str) -> MemoryNode:
        """Build hierarchical memory tree from document"""
        # Split into chunks
        chunks = self._split_into_chunks(document)
        
        # Create leaf nodes
        leaf_nodes = [
            MemoryNode(
                content=chunk,
                embedding=self.model.encode(chunk),
                children=[],
                summary=self._generate_summary(chunk)
            )
            for chunk in chunks
        ]
        
        # Build tree bottom-up
        return self._build_tree_recursive(leaf_nodes)
    
    def _split_into_chunks(self, text: str) -> List[str]:
        """Split text into semantic chunks"""
        # TODO: Implement smarter chunking (e.g., by paragraphs, sections)
        words = text.split()
        chunks = []
        for i in range(0, len(words), self.chunk_size):
            chunk = " ".join(words[i:i + self.chunk_size])
            chunks.append(chunk)
        return chunks
    
    def _generate_summary(self, text: str) -> str:
        """Generate concise summary of text chunk"""
        # TODO: Implement summarization (can use LLM)
        return text[:200] + "..."
    
    def _build_tree_recursive(self, nodes: List[MemoryNode], max_children=4) -> MemoryNode:
        """Build tree recursively by clustering similar nodes"""
        if len(nodes) <= max_children:
            summary = self._generate_summary(" ".join(n.content for n in nodes))
            embedding = np.mean([n.embedding for n in nodes], axis=0)
            return MemoryNode(content="", embedding=embedding, children=nodes, summary=summary)
            
        # Cluster nodes into groups
        groups = self._cluster_nodes(nodes, max_children)
        
        # Recursively build subtrees
        parent_nodes = [self._build_tree_recursive(group) for group in groups]
        
        # Create root node
        return self._build_tree_recursive(parent_nodes)
    
    def _cluster_nodes(self, nodes: List[MemoryNode], k: int) -> List[List[MemoryNode]]:
        """Cluster nodes based on embedding similarity"""
        # TODO: Implement clustering (e.g., k-means on embeddings)
        # For now, just split into k groups
        n = len(nodes)
        size = n // k
        groups = []
        for i in range(0, n, size):
            groups.append(nodes[i:i + size])
        return groups 