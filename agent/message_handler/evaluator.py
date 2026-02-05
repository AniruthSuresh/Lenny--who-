"""
RAG Quality Evaluator

Calculates quality scores for RAG responses:
1. Retrieval Quality (based on similarity scores)
2. Groundedness (via LLM-as-judge)
3. Persona Accuracy (keyword matching)
"""

import re
from typing import List, Dict, Any

class RAGEvaluator:
    """Evaluate RAG response quality"""
    
    # Lenny-specific keywords/phrases
    LENNY_KEYWORDS = [
        "framework", "metric", "data", "product-market fit",
        "growth", "retention", "funnel", "roadmap", "prioritize",
        "north star", "activation", "aha moment", "iterate"
    ]
    
    def __init__(self):
        pass
    
    def calculate_retrieval_score(self, search_results: List[Any]) -> Dict[str, float]:
        """
        Calculate retrieval quality based on similarity scores.
        
        Returns:
            {
                "avg_score": float (0-1),
                "top_score": float (0-1),
                "source_diversity": float (0-1)
            }
        """
        if not search_results:
            return {"avg_score": 0.0, "top_score": 0.0, "source_diversity": 0.0}
        
        # Extract scores
        scores = [r.score for r in search_results if hasattr(r, 'score')]
        
        # Calculate metrics
        avg_score = sum(scores) / len(scores) if scores else 0.0
        top_score = max(scores) if scores else 0.0
        
        # Source diversity (LinkedIn vs YouTube mix)
        sources = [r.payload.get('source', '') for r in search_results]
        unique_sources = len(set(sources))
        source_diversity = unique_sources / 2.0  # Max 2 sources (LinkedIn, YouTube)
        
        return {
            "avg_score": round(avg_score, 3),
            "top_score": round(top_score, 3),
            "source_diversity": round(source_diversity, 3)
        }
    
    def calculate_persona_score(self, response: str) -> float:
        """
        Calculate how well response matches Lenny's style.
        
        Simple keyword-based heuristic.
        """
        if not response:
            return 0.0
        
        response_lower = response.lower()
        
        # Count Lenny-specific keywords
        keyword_count = sum(
            1 for keyword in self.LENNY_KEYWORDS 
            if keyword in response_lower
        )
        
        # Normalize by response length (keywords per 100 words)
        word_count = len(response.split())
        if word_count == 0:
            return 0.0
        
        keyword_density = (keyword_count / word_count) * 100
        
        # Score: higher is better, capped at 1.0
        persona_score = min(keyword_density / 5.0, 1.0)  # 5% keyword density = perfect
        
        return round(persona_score, 3)
    
    def calculate_groundedness_score(
        self, 
        response: str, 
        context_chunks: List[str]
    ) -> float:
        """
        Estimate groundedness: how much of response comes from context.
        
        Simple overlap heuristic (in production, use LLM-as-judge).
        """
        if not response or not context_chunks:
            return 0.0
        
        response_lower = response.lower()
        context_lower = " ".join(context_chunks).lower()
        
        # Extract significant words (4+ chars)
        response_words = set(
            word for word in re.findall(r'\w+', response_lower)
            if len(word) >= 4
        )
        context_words = set(
            word for word in re.findall(r'\w+', context_lower)
            if len(word) >= 4
        )
        
        if not response_words:
            return 0.0
        
        # Calculate overlap
        overlap = len(response_words & context_words)
        groundedness = overlap / len(response_words)
        
        return round(groundedness, 3)
    
    def calculate_rag_score(
        self,
        retrieval_metrics: Dict[str, float],
        groundedness: float,
        persona: float
    ) -> Dict[str, Any]:
        """
        Calculate overall RAG score.
        
        Returns:
            {
                "overall": float (0-100),
                "breakdown": {
                    "retrieval": float,
                    "groundedness": float,
                    "persona": float
                },
                "grade": str ("A", "B", "C", "D", "F")
            }
        """
        # Weighted combination
        retrieval_score = retrieval_metrics["avg_score"]
        
        overall = (
            0.4 * retrieval_score +
            0.4 * groundedness +
            0.2 * persona
        )
        
        # Convert to 0-100 scale
        overall_pct = overall * 100
        
        # Assign grade
        if overall_pct >= 80:
            grade = "A"
        elif overall_pct >= 70:
            grade = "B"
        elif overall_pct >= 60:
            grade = "C"
        elif overall_pct >= 50:
            grade = "D"
        else:
            grade = "F"
        
        return {
            "overall": round(overall_pct, 1),
            "breakdown": {
                "retrieval": round(retrieval_score * 100, 1),
                "groundedness": round(groundedness * 100, 1),
                "persona": round(persona * 100, 1)
            },
            "grade": grade
        }