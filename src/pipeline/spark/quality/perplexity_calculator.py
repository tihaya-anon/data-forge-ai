"""
Perplexity Calculator module for DataForge AI platform.
Uses KenLM for calculating text perplexity.
"""

import logging
from typing import Optional


class PerplexityCalculator:
    """
    Calculates text perplexity using KenLM models.
    Perplexity measures how well a probability model predicts a sample.
    Lower perplexity indicates better fluency and coherence.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the perplexity calculator
        
        Args:
            model_path: Optional path to KenLM model file
        """
        self.logger = logging.getLogger(__name__)
        
        try:
            import kenlm
            self.kenlm_available = True
            self.model = None
            
            if model_path:
                self.load_model(model_path)
            else:
                # In production, you would load a pre-trained model
                self.logger.warning("No KenLM model provided. Using mock implementation.")
                
        except ImportError:
            self.kenlm_available = False
            self.logger.warning(
                "kenlm library not found. Using mock implementation. "
                "Install with 'pip install kenlm'"
            )

    def load_model(self, model_path: str):
        """
        Load a KenLM model from file
        
        Args:
            model_path: Path to KenLM model file
        """
        if self.kenlm_available:
            import kenlm
            try:
                self.model = kenlm.Model(model_path)
                self.logger.info(f"Successfully loaded KenLM model from {model_path}")
            except Exception as e:
                self.logger.error(f"Failed to load KenLM model: {e}")
                self.kenlm_available = False
        else:
            self.logger.error("Cannot load model: kenlm library not available")

    def calculate(self, text: str) -> float:
        """
        Calculate perplexity for given text
        
        Args:
            text: Input text string
            
        Returns:
            Perplexity score (lower is better)
        """
        if not text:
            return float('inf')
            
        # If KenLM is available, use it for actual calculation
        if self.kenlm_available and self.model:
            try:
                # Calculate perplexity using KenLM
                score = self.model.perplexity(text)
                return score
            except Exception as e:
                self.logger.error(f"Error calculating perplexity: {e}")
        
        # Mock implementation if KenLM is not available
        # This is a simplified approach for demonstration purposes
        words = text.split()
        if len(words) == 0:
            return float('inf')
        
        # A simple mock calculation based on text characteristics
        # In reality, perplexity calculation requires a trained language model
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        unique_words_ratio = len(set(words)) / len(words) if words else 0
        
        # Mock perplexity calculation
        # In real scenario, this would come from a trained LM
        mock_perplexity = 100.0 + (10.0 * (1 - unique_words_ratio)) + (5.0 * avg_word_length)
        
        return mock_perplexity

    def calculate_batch(self, texts: list) -> list:
        """
        Calculate perplexity for a batch of texts
        
        Args:
            texts: List of input text strings
            
        Returns:
            List of perplexity scores
        """
        return [self.calculate(text) for text in texts]