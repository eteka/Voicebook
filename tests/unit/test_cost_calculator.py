"""
Unit tests for cost calculation utilities.
"""

import pytest
from src.utils.cost_calculator import CostCalculator, get_cost_warning_message


class TestCostCalculator:
    """Test suite for CostCalculator class."""

    def test_pricing_constants(self):
        """Test that pricing constants are defined correctly."""
        assert CostCalculator.PRICING["standard"] == 15.00
        assert CostCalculator.PRICING["hd"] == 30.00

    def test_estimate_cost_standard_quality(self):
        """Test cost estimation for standard quality."""
        # 1 million characters at $15/1M = $15
        text = "A" * 1_000_000
        cost = CostCalculator.estimate_cost(text, "standard")
        assert cost == 15.00

    def test_estimate_cost_hd_quality(self):
        """Test cost estimation for HD quality."""
        # 1 million characters at $30/1M = $30
        text = "A" * 1_000_000
        cost = CostCalculator.estimate_cost(text, "hd")
        assert cost == 30.00

    def test_estimate_cost_small_text(self):
        """Test cost estimation for small text."""
        text = "Hello, world!"  # 13 characters
        cost = CostCalculator.estimate_cost(text, "standard")
        # 13 / 1,000,000 * 15 = 0.000195
        assert cost == 0.0002  # Rounded to 4 decimal places

    def test_estimate_cost_empty_text(self):
        """Test cost estimation for empty text."""
        cost = CostCalculator.estimate_cost("", "standard")
        assert cost == 0.0

    def test_estimate_cost_medium_text(self, sample_text):
        """Test cost estimation with sample text."""
        cost = CostCalculator.estimate_cost(sample_text, "standard")
        assert cost > 0
        assert cost < 1.0  # Sample text shouldn't be that expensive

    @pytest.mark.parametrize("quality,expected_rate", [
        ("standard", 15.00),
        ("hd", 30.00),
    ])
    def test_estimate_cost_different_qualities(self, quality, expected_rate):
        """Test cost estimation across different quality levels."""
        text = "A" * 100_000  # 100K characters
        cost = CostCalculator.estimate_cost(text, quality)
        expected = round((100_000 / 1_000_000) * expected_rate, 4)
        assert cost == expected

    def test_estimate_cost_invalid_quality_defaults_to_standard(self):
        """Test that invalid quality falls back to standard."""
        text = "A" * 1_000_000
        cost = CostCalculator.estimate_cost(text, "invalid_quality")
        assert cost == 15.00  # Should default to standard

    def test_format_cost_small_values(self):
        """Test cost formatting for small values."""
        assert CostCalculator.format_cost(0.0001) == "$0.0001"
        assert CostCalculator.format_cost(0.0050) == "$0.0050"
        assert CostCalculator.format_cost(0.0099) == "$0.0099"

    def test_format_cost_large_values(self):
        """Test cost formatting for values >= $0.01."""
        assert CostCalculator.format_cost(0.01) == "$0.01"
        assert CostCalculator.format_cost(1.00) == "$1.00"
        assert CostCalculator.format_cost(15.50) == "$15.50"
        assert CostCalculator.format_cost(100.99) == "$100.99"

    def test_format_cost_rounding(self):
        """Test cost formatting rounds correctly."""
        assert CostCalculator.format_cost(1.234) == "$1.23"
        assert CostCalculator.format_cost(1.235) == "$1.24"  # Round up
        assert CostCalculator.format_cost(1.999) == "$2.00"

    def test_characters_per_dollar_standard(self):
        """Test characters per dollar for standard quality."""
        chars = CostCalculator.characters_per_dollar("standard")
        # 1,000,000 / 15 = 66,666
        assert chars == 66666

    def test_characters_per_dollar_hd(self):
        """Test characters per dollar for HD quality."""
        chars = CostCalculator.characters_per_dollar("hd")
        # 1,000,000 / 30 = 33,333
        assert chars == 33333

    def test_characters_per_dollar_invalid_defaults_to_standard(self):
        """Test characters per dollar with invalid quality."""
        chars = CostCalculator.characters_per_dollar("invalid")
        assert chars == 66666  # Should default to standard

    def test_estimate_words_to_cost_standard(self):
        """Test word count to cost estimation for standard quality."""
        # 1000 words * 5 chars = 5000 chars
        # 5000 / 1,000,000 * 15 = 0.075
        cost = CostCalculator.estimate_words_to_cost(1000, "standard")
        assert cost == 0.075

    def test_estimate_words_to_cost_hd(self):
        """Test word count to cost estimation for HD quality."""
        # 1000 words * 5 chars = 5000 chars
        # 5000 / 1,000,000 * 30 = 0.15
        cost = CostCalculator.estimate_words_to_cost(1000, "hd")
        assert cost == 0.15

    @pytest.mark.parametrize("words,quality,expected", [
        (100, "standard", 0.0075),     # 500 chars
        (1000, "standard", 0.075),     # 5000 chars
        (10000, "standard", 0.75),     # 50000 chars
        (100, "hd", 0.015),            # 500 chars
        (1000, "hd", 0.15),            # 5000 chars
    ])
    def test_estimate_words_to_cost_parametrized(self, words, quality, expected):
        """Test various word counts and quality combinations."""
        cost = CostCalculator.estimate_words_to_cost(words, quality)
        assert cost == expected

    def test_estimate_words_to_cost_zero_words(self):
        """Test zero words returns zero cost."""
        cost = CostCalculator.estimate_words_to_cost(0, "standard")
        assert cost == 0.0


class TestCostWarningMessage:
    """Test suite for get_cost_warning_message function."""

    def test_warning_below_threshold(self):
        """Test no warning when cost is below threshold."""
        message = get_cost_warning_message(1.99, threshold=2.00)
        assert message == ""

    def test_warning_at_threshold(self):
        """Test warning when cost equals threshold."""
        message = get_cost_warning_message(2.00, threshold=2.00)
        assert message != ""
        assert "⚠️" in message
        assert "$2.00" in message

    def test_warning_above_threshold(self):
        """Test warning when cost exceeds threshold."""
        message = get_cost_warning_message(5.00, threshold=2.00)
        assert message != ""
        assert "⚠️" in message
        assert "$5.00" in message
        assert "High Cost Warning" in message

    def test_warning_custom_threshold(self):
        """Test warning with custom threshold."""
        message = get_cost_warning_message(0.50, threshold=0.25)
        assert message != ""
        assert "$0.50" in message

    def test_warning_message_format(self):
        """Test warning message contains expected elements."""
        message = get_cost_warning_message(10.00, threshold=2.00)
        assert "⚠️" in message
        assert "High Cost Warning" in message
        assert "approximately" in message
        assert "$10.00" in message

    @pytest.mark.parametrize("cost,threshold,should_warn", [
        (0.01, 2.00, False),
        (1.99, 2.00, False),
        (2.00, 2.00, True),
        (2.01, 2.00, True),
        (100.00, 2.00, True),
        (0.50, 0.50, True),
        (0.49, 0.50, False),
    ])
    def test_warning_threshold_conditions(self, cost, threshold, should_warn):
        """Test various cost and threshold combinations."""
        message = get_cost_warning_message(cost, threshold)
        if should_warn:
            assert message != ""
            assert "⚠️" in message
        else:
            assert message == ""


class TestCostCalculatorIntegration:
    """Integration tests for cost calculation workflow."""

    def test_full_workflow_standard(self):
        """Test complete cost calculation workflow for standard quality."""
        text = "This is a test document. " * 1000  # ~25,000 chars
        cost = CostCalculator.estimate_cost(text, "standard")
        formatted = CostCalculator.format_cost(cost)
        warning = get_cost_warning_message(cost, threshold=1.00)

        assert cost > 0
        assert "$" in formatted
        # Cost should be around $0.38 (25000/1000000 * 15)
        assert 0.35 < cost < 0.40

    def test_full_workflow_hd(self):
        """Test complete cost calculation workflow for HD quality."""
        text = "Test. " * 50000  # ~300,000 chars
        cost = CostCalculator.estimate_cost(text, "hd")
        formatted = CostCalculator.format_cost(cost)
        warning = get_cost_warning_message(cost, threshold=2.00)

        assert cost > 0
        assert "$" in formatted
        # Cost should be around $9.00 (300000/1000000 * 30)
        assert 8.0 < cost < 10.0
        # Should trigger warning
        assert warning != ""
        assert "⚠️" in warning

    def test_cost_comparison_standard_vs_hd(self):
        """Test that HD costs exactly 2x standard for same text."""
        text = "Sample text for comparison testing."
        cost_standard = CostCalculator.estimate_cost(text, "standard")
        cost_hd = CostCalculator.estimate_cost(text, "hd")

        assert cost_hd == cost_standard * 2

    def test_realistic_book_chapter_cost(self):
        """Test cost estimation for a realistic book chapter (~5000 words)."""
        # Average book chapter: 5000 words
        cost_standard = CostCalculator.estimate_words_to_cost(5000, "standard")
        cost_hd = CostCalculator.estimate_words_to_cost(5000, "hd")

        # 5000 words * 5 chars = 25,000 chars
        # Standard: 25,000 / 1,000,000 * 15 = $0.375
        # HD: 25,000 / 1,000,000 * 30 = $0.75
        assert 0.37 <= cost_standard <= 0.38
        assert 0.74 <= cost_hd <= 0.76

        # Should not trigger default $2 warning
        assert get_cost_warning_message(cost_standard) == ""
        assert get_cost_warning_message(cost_hd) == ""

    def test_realistic_full_book_cost(self):
        """Test cost estimation for a full book (~80,000 words)."""
        # Average novel: 80,000 words
        cost_standard = CostCalculator.estimate_words_to_cost(80000, "standard")
        cost_hd = CostCalculator.estimate_words_to_cost(80000, "hd")

        # 80,000 words * 5 chars = 400,000 chars
        # Standard: 400,000 / 1,000,000 * 15 = $6.00
        # HD: 400,000 / 1,000,000 * 30 = $12.00
        assert cost_standard == 6.00
        assert cost_hd == 12.00

        # Should trigger default $2 warning
        assert get_cost_warning_message(cost_standard) != ""
        assert get_cost_warning_message(cost_hd) != ""
