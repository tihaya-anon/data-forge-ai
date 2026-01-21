"""
Toxicity Detector module for DataForge AI platform.
Detects toxic content in text using classification models.
"""

import logging
from typing import Optional, Union
import re


class ToxicityDetector:
    """
    Detects toxicity in text content.
    Uses pattern matching and ML-based approaches for toxicity detection.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the toxicity detector
        
        Args:
            model_path: Optional path to toxicity detection model
        """
        self.logger = logging.getLogger(__name__)
        
        # Basic toxicity patterns (words/phrases that indicate toxicity)
        self.toxic_patterns = [
            r'\b(?:hate|kill|murder|destroy|attack|violence|abuse)\b',
            r'\b(?:stupid|dumb|idiot|moron|fool|worthless)\b',
            r'\b(?:harmful|dangerous|threatening|menacing)\b',
            # Note: These are example patterns only
            # Real implementation would use a trained classifier
        ]
        
        # Try to initialize ML model if available
        self.ml_model = None
        self.use_ml_model = False
        
        try:
            # Attempt to load a machine learning model
            # This could be a transformer model fine-tuned for toxicity detection
            import transformers
            import torch
            
            # For now, we'll just log that we could load a model
            self.logger.info("Transformer library available for toxicity detection")
            
            # In a real implementation, you would load a pre-trained model like:
            # self.ml_model = transformers.pipeline(
            #     "text-classification",
            #     model="unitary/toxic-bert",
            #     tokenizer="unitary/toxic-bert"
            # )
            # self.use_ml_model = True
            
        except ImportError:
            self.logger.warning(
                "Transformers or PyTorch not available. Using basic pattern matching."
            )
    
    def detect(self, text: str) -> float:
        """
        Detect toxicity in the given text
        
        Args:
            text: Input text string
            
        Returns:
            Toxicity score between 0 and 1 (higher is more toxic)
        """
        if not text:
            return 0.0
        
        # Convert to lowercase for comparison
        lower_text = text.lower()
        
        # If ML model is available, use it
        if self.use_ml_model and self.ml_model:
            try:
                result = self.ml_model(text)
                # Assuming the model returns a dictionary with 'score' key
                # for the toxicity label
                return result[0]['score'] if result[0]['label'] == 'TOXIC' else 1 - result[0]['score']
            except Exception as e:
                self.logger.error(f"Error using ML model for toxicity detection: {e}")
        
        # Fallback to pattern matching approach
        toxic_matches = 0
        for pattern in self.toxic_patterns:
            if re.search(pattern, lower_text):
                toxic_matches += 1
        
        # Calculate a simple toxicity score based on patterns matched
        # This is a mock implementation - real implementation would use a trained model
        score = min(toxic_matches / max(len(self.toxic_patterns), 1), 1.0)
        
        # Additional heuristics for toxicity detection
        # Check for excessive punctuation or capitalization
        exclamation_count = text.count('!')
        question_count = text.count('?')
        caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if text else 0
        
        # Increase score if text seems aggressive
        if exclamation_count > 3 or caps_ratio > 0.7:
            score = min(score + 0.2, 1.0)
        
        # Check for profanity-like patterns (these are just examples)
        profanity_indicators = ['shit', 'damn', 'hell', 'fuck', 'bitch', 'asshole']
        profanity_count = sum(1 for word in profanity_indicators if word in lower_text)
        if profanity_count > 0:
            score = min(score + (profanity_count * 0.1), 1.0)
        
        return score
    
    def detect_batch(self, texts: list) -> list:
        """
        Detect toxicity for a batch of texts
        
        Args:
            texts: List of input text strings
            
        Returns:
            List of toxicity scores
        """
        return [self.detect(text) for text in texts]
    
    def is_toxic(self, text: str, threshold: float = 0.5) -> bool:
        """
        Check if text is toxic based on a threshold
        
        Args:
            text: Input text string
            threshold: Toxicity threshold (above this is considered toxic)
            
        Returns:
            True if text is toxic, False otherwise
        """
        return self.detect(text) >= threshold