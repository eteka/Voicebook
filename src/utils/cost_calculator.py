"""
Cost calculation utilities for OpenAI TTS API.

Pricing (as of 2024):
- tts-1 (standard): $15.00 per 1M characters
- tts-1-hd (HD): $30.00 per 1M characters
"""

class CostCalculator:
    """Calculate TTS generation costs."""

    # Pricing per 1 million characters (USD)
    PRICING = {
        "standard": 15.00,  # tts-1
        "hd": 30.00         # tts-1-hd
    }

    @staticmethod
    def estimate_cost(text: str, quality: str = "standard") -> float:
        """
        Calculate estimated cost for generating audio from text.

        Args:
            text: Input text to convert
            quality: "standard" (tts-1) or "hd" (tts-1-hd)

        Returns:
            Estimated cost in USD
        """
        char_count = len(text)
        rate = CostCalculator.PRICING.get(quality, CostCalculator.PRICING["standard"])
        cost = (char_count / 1_000_000) * rate
        return round(cost, 4)

    @staticmethod
    def format_cost(cost: float) -> str:
        """Format cost for display."""
        if cost < 0.01:
            return f"${cost:.4f}"
        return f"${cost:.2f}"

    @staticmethod
    def characters_per_dollar(quality: str = "standard") -> int:
        """Calculate how many characters you get per dollar."""
        rate = CostCalculator.PRICING.get(quality, CostCalculator.PRICING["standard"])
        return int(1_000_000 / rate)

    @staticmethod
    def estimate_words_to_cost(words: int, quality: str = "standard") -> float:
        """
        Estimate cost based on word count (assumes avg 5 chars per word).

        Args:
            words: Number of words
            quality: "standard" or "hd"

        Returns:
            Estimated cost in USD
        """
        # Average word length in English is ~4.7 chars, we use 5 for safety
        estimated_chars = words * 5
        return CostCalculator.estimate_cost("x" * estimated_chars, quality)


def get_cost_warning_message(cost: float, threshold: float = 2.00) -> str:
    """
    Generate a warning message if cost exceeds threshold.

    Args:
        cost: Estimated cost
        threshold: Warning threshold

    Returns:
        Warning message or empty string
    """
    if cost >= threshold:
        return f"⚠️ High Cost Warning: This will cost approximately {CostCalculator.format_cost(cost)}"
    return ""
