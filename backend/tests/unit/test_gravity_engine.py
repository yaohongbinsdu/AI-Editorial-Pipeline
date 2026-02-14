"""T084: Unit tests for gravity engine service."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.gravity_engine import GravityEngine, GravitySchema, compute_composite_score


class TestGravitySchema:
    def test_has_16_dimensions(self):
        """GravitySchema should have all 16 dimensions + vote + gate."""
        fields = GravitySchema.model_fields
        expected_dims = [
            "industry_impact", "consumer_impact", "actionability", "risk_urgency",
            "novelty", "technical_depth", "second_order_potential", "builder_relevance",
            "entertainment_value", "signal_to_noise", "viral_potential", "early_trend_signal",
            "pr_fluff", "speculation", "concreteness", "paid_sponsorship",
        ]
        for dim in expected_dims:
            assert dim in fields, f"Missing dimension: {dim}"
        assert "editorial_vote" in fields
        assert "novelty_gate" in fields
        assert "reasoning" in fields

    def test_validation(self):
        valid_data = {
            "industry_impact": 7.0, "consumer_impact": 5.0,
            "actionability": 6.0, "risk_urgency": 4.0,
            "novelty": 8.0, "technical_depth": 7.0,
            "second_order_potential": 5.0, "builder_relevance": 6.0,
            "entertainment_value": 4.0, "signal_to_noise": 8.0,
            "viral_potential": 6.0, "early_trend_signal": 7.0,
            "pr_fluff": 2.0, "speculation": 3.0,
            "concreteness": 7.0, "paid_sponsorship": 1.0,
            "editorial_vote": "interesting",
            "novelty_gate": True,
            "reasoning": "Test reasoning",
        }
        schema = GravitySchema(**valid_data)
        assert schema.editorial_vote == "interesting"
        assert schema.novelty_gate is True

    def test_invalid_vote_falls_back_to_skip(self):
        data = {
            "industry_impact": 5.0, "consumer_impact": 5.0,
            "actionability": 5.0, "risk_urgency": 5.0,
            "novelty": 5.0, "technical_depth": 5.0,
            "second_order_potential": 5.0, "builder_relevance": 5.0,
            "entertainment_value": 5.0, "signal_to_noise": 5.0,
            "viral_potential": 5.0, "early_trend_signal": 5.0,
            "pr_fluff": 5.0, "speculation": 5.0,
            "concreteness": 5.0, "paid_sponsorship": 5.0,
            "editorial_vote": "invalid_vote",
            "novelty_gate": False,
        }
        schema = GravitySchema(**data)
        assert schema.editorial_vote == "skip"


class TestCompositeScore:
    def test_computation(self):
        """compute_composite_score should produce a value in [0, 10]."""
        schema = GravitySchema(
            industry_impact=8.0, consumer_impact=6.0,
            actionability=7.0, risk_urgency=5.0,
            novelty=9.0, technical_depth=7.0,
            second_order_potential=6.0, builder_relevance=7.0,
            entertainment_value=5.0, signal_to_noise=8.0,
            viral_potential=7.0, early_trend_signal=6.0,
            pr_fluff=2.0, speculation=3.0,
            concreteness=8.0, paid_sponsorship=1.0,
            editorial_vote="interesting", novelty_gate=True,
        )
        result = compute_composite_score(schema)
        assert isinstance(result, float)
        assert 0 <= result <= 10


class TestGravityEngine:
    def test_class_exists(self):
        with patch("app.services.gravity_engine.settings") as mock_settings:
            mock_settings.ANTHROPIC_API_KEY = "test-key"
            engine = GravityEngine()
            assert hasattr(engine, "score_article")
            assert hasattr(engine, "score_and_update")
