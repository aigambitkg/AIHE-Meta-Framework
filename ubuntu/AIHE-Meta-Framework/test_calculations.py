import pytest
from decimal import Decimal

from app.core.calculations import AIHECalculationEngine, DynamicWeightingEngine, GapAnalysisEngine, Archetyp, DimensionScore, ContextFactor

# Sample data for testing based on the complete specification
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
    """Provides a sample list of ContextFactor objects for testing (10 factors F1-F10)."""
    return [
        ContextFactor(factor_name='Organisationsgröße', factor_value=2),
        ContextFactor(factor_name='Branchendynamik', factor_value=1),
        ContextFactor(factor_name='Regulatorischer Druck', factor_value=3),
        ContextFactor(factor_name='Technologische Komplexität', factor_value=2),
        ContextFactor(factor_name='Change-Historie', factor_value=1),
        ContextFactor(factor_name='Marktdynamik', factor_value=2),
        ContextFactor(factor_name='Wettbewerbsdruck', factor_value=3),
        ContextFactor(factor_name='Ressourcenverfügbarkeit', factor_value=2), # Inverted, so becomes 1
        ContextFactor(factor_name='Digitalisierungsgrad', factor_value=1),
        ContextFactor(factor_name='Innovationsdruck', factor_value=2),
    ]


class TestAIHECalculationEngine:
    """Tests for the main AIHE calculation engine based on complete specification."""

    def test_calculate_eqi(self, sample_dimension_scores):
        """Test the Equilibrium Quality Index (EQI) calculation."""
        # Total gap = 0.5 + 0.4 + 1.2 + 2.0 + 0.7 + 0.5 + 0.3 + 1.0 = 6.6
        # EQI = 1 - (6.6 / 24.0) = 1 - 0.275 = 0.725
        eqi = AIHECalculationEngine.calculate_eqi(sample_dimension_scores)
        assert eqi == pytest.approx(0.725, abs=1e-3)

    def test_calculate_rgi(self, sample_dimension_scores):
        """Test the Reifegrad-Index (RGI) calculation."""
        # Weighted sum = 2.5*0.20 + 2.8*0.18 + 1.8*0.10 + 1.5*0.12 + 2.3*0.12 + 3.5*0.08 + 2.7*0.10 + 2.0*0.10
        # = 0.5 + 0.504 + 0.18 + 0.18 + 0.276 + 0.28 + 0.27 + 0.20 = 2.39
        # RGI = 2.39 / 4.0 = 0.5975
        rgi = AIHECalculationEngine.calculate_rgi(sample_dimension_scores)
        assert rgi == pytest.approx(0.5975, abs=1e-3)

    def test_calculate_si(self, sample_dimension_scores):
        """Test the Spannungsindex (SI) calculation."""
        # Based on 12 tension pairs from specification
        si = AIHECalculationEngine.calculate_si(sample_dimension_scores)
        # SI should be between 0 and 1
        assert 0.0 <= si <= 1.0

    def test_calculate_sbs(self):
        """Test the System Balance Score (SBS) calculation."""
        eqi = 0.725
        si = 0.308
        rgi = 0.5975
        # SBS = (EQI + (1-SI) + RGI) / 3 = (0.725 + 0.692 + 0.5975) / 3 = 0.6715
        sbs = AIHECalculationEngine.calculate_sbs(eqi, si, rgi)
        assert sbs == pytest.approx(0.6715, abs=1e-3)

    def test_calculate_context_score(self, sample_context_factors):
        """Test the Context Score calculation with 10 factors."""
        context_score = AIHECalculationEngine.calculate_context_score(sample_context_factors)
        # Should be between 0 and 1
        assert 0.0 <= context_score <= 1.0


class TestDynamicWeightingEngine:
    """Tests for the dynamic weighting engine with 8 rules."""

    def test_calculate_dynamic_weights_chaotic_doer(self, sample_dimension_scores):
        """Test weight calculation for the CHAOTIC_DOER archetype."""
        weights = DynamicWeightingEngine.calculate_dynamic_weights(
            dimension_scores=sample_dimension_scores,
            context_score=0.625,
            archetyp=Archetyp.CHAOTIC_DOER
        )
        
        # Verify sum equals 1.0
        assert sum(weights.values()) == pytest.approx(1.0, abs=1e-3)
        
        # Verify all weights are positive
        for weight in weights.values():
            assert weight > 0
        
        # Verify minimum weight constraint (1%)
        for weight in weights.values():
            assert weight >= 0.01

    def test_calculate_dynamic_weights_balanced_transformer(self, sample_dimension_scores):
        """Test weight calculation for the BALANCED_TRANSFORMER archetype."""
        weights = DynamicWeightingEngine.calculate_dynamic_weights(
            dimension_scores=sample_dimension_scores,
            context_score=0.5,  # Neutral context
            archetyp=Archetyp.BALANCED_TRANSFORMER
        )
        
        # Verify sum equals 1.0
        assert sum(weights.values()) == pytest.approx(1.0, abs=1e-3)
        
        # All weights should be relatively balanced for this archetype
        weight_values = list(weights.values())
        max_weight = max(weight_values)
        min_weight = min(weight_values)
        # Difference should not be too extreme after adjustments
        assert (max_weight - min_weight) < 0.3

    def test_load_base_weights_kmu(self):
        """Test loading of KMU-specific base weights."""
        weights = DynamicWeightingEngine._load_base_weights(is_kmu=True)
        
        # Verify KMU-specific adjustments
        assert weights["D2"] > weights["D1"]  # Strategy more important than governance for KMU
        assert weights["D3"] > weights["D5"]  # Culture more important than data for KMU
        assert weights["D7"] > weights["D8"]  # Processes more important than impact for KMU

    def test_load_base_weights_standard(self):
        """Test loading of standard base weights."""
        weights = DynamicWeightingEngine._load_base_weights(is_kmu=False)
        
        # All weights should be equal for standard approach
        for weight in weights.values():
            assert weight == pytest.approx(0.125, abs=1e-3)

    def test_archetyp_factors(self):
        """Test archetyp-specific factors."""
        # Test CHAOTIC_DOER factors
        factors = DynamicWeightingEngine._get_archetyp_factors(Archetyp.CHAOTIC_DOER)
        assert factors["D1"] > 1.0  # Leadership should be strengthened
        assert factors["D6"] < 1.0  # Tech should be dampened (already good)
        
        # Test CAUTIOUS_CORPORATE factors
        factors = DynamicWeightingEngine._get_archetyp_factors(Archetyp.CAUTIOUS_CORPORATE)
        assert factors["D3"] > 1.0  # Culture should be strengthened
        assert factors["D1"] < 1.0  # Leadership should be dampened (already good)

    def test_minimum_security(self):
        """Test minimum security rule (no weight below 1%)."""
        # Create weights with some very small values
        weights = {
            "D1": Decimal("0.005"),  # Below minimum
            "D2": Decimal("0.2"),
            "D3": Decimal("0.3"),
            "D4": Decimal("0.495"),  # Sum would be 1.0 without adjustment
        }
        
        adjusted_weights = DynamicWeightingEngine._apply_minimum_security(weights)
        
        # Check that minimum weight is enforced
        assert adjusted_weights["D1"] == Decimal("0.01")

    def test_normalization(self):
        """Test weight normalization to sum to 1.0."""
        # Create weights that don't sum to 1.0
        weights = {
            "D1": Decimal("0.3"),
            "D2": Decimal("0.4"),
            "D3": Decimal("0.5"),  # Sum = 1.2
        }
        
        normalized = DynamicWeightingEngine._normalize_weights(weights)
        
        # Check that sum equals 1.0
        assert sum(normalized.values()) == pytest.approx(1.0, abs=1e-6)


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
        (1.9, 1.6, "CRITICAL"),  # Low ist + high gap
        (2.4, 1.1, "HIGH"),      # Medium ist + medium gap
        (2.6, 1.6, "HIGH"),      # Medium ist + high gap
        (3.0, 0.9, "HIGH"),      # Good ist + medium gap
        (3.5, 0.5, "MEDIUM"),    # High ist + small gap
        (3.8, 0.2, "LOW"),       # Very high ist + very small gap
    ])
    def test_calculate_priority_level(self, ist, gap, expected_priority):
        """Test the priority level calculation."""
        priority = GapAnalysisEngine.calculate_priority_level(ist, gap)
        assert priority == expected_priority

    def test_generate_recommendations(self, sample_dimension_scores):
        """Test generation of recommendations based on gap analysis."""
        recommendations = GapAnalysisEngine.generate_recommendations(sample_dimension_scores)
        
        # Should return recommendations for critical/high priority items
        assert len(recommendations) > 0
        
        # Check that recommendations are sorted by priority
        for i in range(len(recommendations) - 1):
            current_priority = recommendations[i]["priority"]
            next_priority = recommendations[i + 1]["priority"]
            
            priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
            assert priority_order[current_priority] <= priority_order[next_priority]
        
        # Check that each recommendation has required fields
        for rec in recommendations:
            assert "dimension_id" in rec
            assert "priority" in rec
            assert "gap" in rec
            assert "gap_percent" in rec
            assert "description" in rec
            assert "ist_value" in rec
            assert "soll_value" in rec
