import pytest
from decimal import Decimal

from app.core.calculations import AIHECalculationEngine, DynamicWeightingEngine, GapAnalysisEngine
from app.models import DimensionScore, ContextFactor, LearningCycle # Import LearningCycle

# Sample data for testing
@pytest.fixture
def sample_dimension_scores():
    """Provides a sample list of DimensionScore objects for testing."""
    return [
        DimensionScore(dimension_id='D1', ist_value=Decimal("2.5"), soll_value=Decimal("3.0"), dynamic_weight=Decimal("0.20")), # Gap: 0.5
        DimensionScore(dimension_id='D2', ist_value=Decimal("2.8"), soll_value=Decimal("3.2"), dynamic_weight=Decimal("0.18")), # Gap: 0.4
        DimensionScore(dimension_id='D3', ist_value=Decimal("1.8"), soll_value=Decimal("3.0"), dynamic_weight=Decimal("0.10")), # Gap: 1.2
        DimensionScore(dimension_id='D4', ist_value=Decimal("1.5"), soll_value=Decimal("3.5"), dynamic_weight=Decimal("0.12")), # Gap: 2.0
        DimensionScore(dimension_id='D5', ist_value=Decimal("2.3"), soll_value=Decimal("3.0"), dynamic_weight=Decimal("0.12")), # Gap: 0.7
        DimensionScore(dimension_id='D6', ist_value=Decimal("3.5"), soll_value=Decimal("3.0"), dynamic_weight=Decimal("0.08")), # Gap: 0.5
        DimensionScore(dimension_id='D7', ist_value=Decimal("2.7"), soll_value=Decimal("3.0"), dynamic_weight=Decimal("0.10")), # Gap: 0.3
        DimensionScore(dimension_id='D8', ist_value=Decimal("2.0"), soll_value=Decimal("3.0"), dynamic_weight=Decimal("0.10")), # Gap: 1.0
    ]

@pytest.fixture
def sample_context_factors():
    """Provides a sample list of ContextFactor objects for testing."""
    return [
        ContextFactor(factor_name='Organisationsgröße', factor_value=2),
        ContextFactor(factor_name='Branchendynamik', factor_value=1),
        ContextFactor(factor_name='Regulatorischer Druck', factor_value=3),
        ContextFactor(factor_name='Technologische Komplexität', factor_value=2),
        ContextFactor(factor_name='Change-Historie', factor_value=1),
        ContextFactor(factor_name='Marktdynamik', factor_value=2),
        ContextFactor(factor_name='Wettbewerbsdruck', factor_value=3),
        ContextFactor(factor_name='Ressourcenverfügbarkeit', factor_value=2), # Inverted, so becomes 1
    ]


class TestAIHECalculationEngine:
    """Tests for the main AIHE calculation engine."""

    def test_calculate_eqi(self, sample_dimension_scores):
        """Test the Equilibrium Quality Index (EQI) calculation."""
        eqi = AIHECalculationEngine.calculate_eqi(sample_dimension_scores)
        assert eqi == 0.725

    def test_calculate_rgi(self, sample_dimension_scores):
        """Test the Reifegrad-Index (RGI) calculation."""
        rgi = AIHECalculationEngine.calculate_rgi(sample_dimension_scores)
        assert rgi == pytest.approx(0.598, abs=1e-3)

    def test_calculate_si(self, sample_dimension_scores):
        """Test the Spannungsindex (SI) calculation."""
        si = AIHECalculationEngine.calculate_si(sample_dimension_scores)
        assert si == pytest.approx(0.157, abs=1e-3)

    def test_calculate_sbs(self):
        """Test the System Balance Score (SBS) calculation."""
        eqi = 0.725
        si = 0.308
        rgi = 0.597
        sbs = AIHECalculationEngine.calculate_sbs(eqi, si, rgi)
        assert sbs == pytest.approx(0.671, abs=1e-3)

    def test_calculate_context_score(self, sample_context_factors):
        """Test the Context Score calculation."""
        context_score = AIHECalculationEngine.calculate_context_score(sample_context_factors)
        assert context_score == 0.625


class TestDynamicWeightingEngine:
    """Tests for the dynamic weighting engine."""

    def test_calculate_dynamic_weights_chaotic_doer(self):
        """Test weight calculation for the CHAOTIC_DOER archetype."""
        weights = DynamicWeightingEngine.calculate_dynamic_weights(
            archetype="CHAOTIC_DOER",
            context_score=0.625 # From previous test
        )
        assert sum(weights.values()) == pytest.approx(1.0)
        assert weights["D1"] > weights["D6"] # Governance > Tech
        assert weights["D1"] == pytest.approx(0.20, abs=1e-3)

    def test_calculate_dynamic_weights_balanced(self):
        """Test weight calculation for the BALANCED_TRANSFORMER archetype."""
        weights = DynamicWeightingEngine.calculate_dynamic_weights(
            archetype="BALANCED_TRANSFORMER",
            context_score=0.5 # Neutral context
        )
        assert sum(weights.values()) == pytest.approx(1.0)
        for weight in weights.values():
            assert weight == pytest.approx(0.125)


class TestGapAnalysisEngine:
    """Tests for the gap analysis and priority calculation engine."""

    @pytest.mark.parametrize("ist, soll, expected_gap, expected_percent", [
        (2.5, 3.0, 0.5, 12.5),
        (1.8, 3.0, 1.2, 30.0),
        (3.5, 3.0, 0.5, 12.5),
        (4.0, 1.0, 3.0, 75.0),
    ])
    def test_calculate_subdimension_gap(self, ist, soll, expected_gap, expected_percent):
        """Test the gap calculation for subdimensions."""
        gap, gap_percent = GapAnalysisEngine.calculate_subdimension_gap(ist, soll)
        assert gap == expected_gap
        assert gap_percent == expected_percent

    @pytest.mark.parametrize("ist, gap, expected_priority", [
        (1.9, 1.6, "CRITICAL"),
        (2.4, 1.1, "HIGH"),
        (2.6, 1.6, "HIGH"),
        (3.0, 0.9, "MEDIUM"),
        (3.5, 0.5, "LOW"),
    ])
    def test_calculate_priority_level(self, ist, gap, expected_priority):
        """Test the priority level calculation."""
        priority = GapAnalysisEngine.calculate_priority_level(ist, gap)
        assert priority == expected_priority

