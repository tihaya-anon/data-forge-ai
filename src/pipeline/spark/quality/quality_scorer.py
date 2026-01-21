"""
Quality Scorer module for DataForge AI platform.
Calculates text quality using fastText or similar models.
"""

import logging
from typing import Optional, List
import re


class QualityScorer:
    """
    Calculates text quality using fastText models or similar approaches.
    Quality score indicates how well-written and informative the text is.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the quality scorer
        
        Args:
            model_path: Optional path to quality scoring model
        """
        self.logger = logging.getLogger(__name__)
        
        # Language detection patterns (for basic validation)
        self.language_patterns = {
            'en': r'[a-zA-Z\s\d\W]',
            # Add more languages as needed
        }
        
        # Initialize fastText if available
        self.fasttext_model = None
        self.fasttext_available = False
        
        try:
            import fasttext
            # In a real implementation, you would load a pre-trained model
            # self.fasttext_model = fasttext.load_model(model_path) if model_path else None
            self.fasttext_available = True
            self.logger.info("fastText library available for quality scoring")
        except ImportError:
            self.logger.warning(
                "fasttext library not found. Using heuristic scoring. "
                "Install with 'pip install fasttext'"
            )
    
    def score(self, text: str) -> float:
        """
        Score the quality of the given text
        
        Args:
            text: Input text string
            
        Returns:
            Quality score between 0 and 1 (higher is better quality)
        """
        if not text:
            return 0.0
        
        # If fastText model is available, use it
        if self.fasttext_available and self.fasttext_model:
            try:
                # Predict using fastText model
                predictions = self.fasttext_model.predict([text])
                # Extract the quality score from predictions
                # Implementation depends on the specific model
                return float(predictions[0][0])  # Simplified - adjust based on model output
            except Exception as e:
                self.logger.error(f"Error using fastText model for quality scoring: {e}")
        
        # Heuristic-based quality scoring as fallback
        return self._calculate_heuristic_score(text)
    
    def _calculate_heuristic_score(self, text: str) -> float:
        """
        Calculate quality score using heuristic methods
        
        Args:
            text: Input text string
            
        Returns:
            Quality score between 0 and 1
        """
        if not text:
            return 0.0
        
        # Calculate various text metrics
        word_count = len(text.split())
        char_count = len(text)
        sentence_count = len(re.split(r'[.!?]+', text)) - 1  # Subtract 1 because split adds an empty string at the end
        
        # Length-based quality factors
        if word_count == 0:
            return 0.0
        
        # Very short texts have low quality
        if word_count < 10:
            return 0.1
        
        # Reward moderate length texts (not too short, not too verbose)
        length_quality = min(1.0, max(0.1, word_count / 100))
        
        # Check for readability: ratio of letters to total characters
        letter_count = sum(c.isalpha() for c in text)
        readability = letter_count / char_count if char_count > 0 else 0
        
        # Check for repetition: compare unique words vs total words
        words = text.lower().split()
        unique_ratio = len(set(words)) / len(words) if words else 0
        
        # Check for special characters ratio (too many might indicate poor quality)
        special_char_ratio = sum(not c.isalnum() and c != ' ' for c in text) / char_count if char_count > 0 else 0
        
        # Check for consecutive repeated characters (e.g., "aaaaaa")
        consecutive_repeats = len(re.findall(r'(.)\1{4,}', text))
        
        # Combine metrics into a final score
        # Each factor contributes to the overall quality score
        score = (
            0.25 * length_quality +
            0.20 * readability +
            0.25 * unique_ratio +
            0.15 * max(0.0, 1.0 - special_char_ratio) +
            0.15 * max(0.0, 1.0 - min(1.0, consecutive_repeats * 0.1))
        )
        
        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, score))
    
    def score_batch(self, texts: List[str]) -> List[float]:
        """
        Score the quality for a batch of texts
        
        Args:
            texts: List of input text strings
            
        Returns:
            List of quality scores
        """
        return [self.score(text) for text in texts]
    
    def classify_quality(self, text: str, thresholds: Optional[dict] = None) -> str:
        """
        Classify text quality level
        
        Args:
            text: Input text string
            thresholds: Optional dict with 'low', 'medium', 'high' keys
            
        Returns:
            Quality level ('low', 'medium', or 'high')
        """
        if thresholds is None:
            thresholds = {'low': 0.3, 'medium': 0.7}
        
        score = self.score(text)
        
        if score < thresholds['low']:
            return 'low'
        elif score < thresholds['medium']:
            return 'medium'
        else:
            return 'high'