"""
Core calculation engine for the AIHE Meta-Framework.

This module implements the mathematical formulas for the 5 core metrics:
- EQI (Equilibrium Quality Index)
- RGI (Reifegrad-Index) 
- SI (Spannungsindex)
- SBS (System Balance Score)
- Context Score
"""

import math
from typing import Dict, List, Tuple
from decimal import Decimal, ROUND_HALF_UP

from app.models.assessment import Assessment, DimensionScore, SubdimensionScore, ContextFactor


class AIHECalculationEngine:
    """
    Main calculation engine for AIHE metrics.
    
    This class implements all mathematical formulas specified in the
    technical documentation for calculating the core metrics.
    """
    
    # Critical tension pairs as defined in the specification
    TENSION_PAIRS = [
        ("D6", "D3"),  # Tech-Kultur-Spannung
        ("D1", "D6"),  # Governance-Innovation
        ("D2", "D4"),  # Strategie-Kompetenz
        ("D5", "D7"),  # Daten-Prozess
        ("D1", "D8"),  # Ethik-Wirkung
        ("D3", "D4"),  # Kultur-Kompetenz
        ("D2", "D1"),  # Strategie-Governance
        ("D6", "D5"),  # Tech-Daten
        ("D7", "D8"),  # Prozess-Wirkung
        ("D3", "D1"),  # Innovation-Governance
        ("D4", "D6"),  # Kompetenz-Tech
        ("D2", "D7"),  # Alignment-Durchführung
    ]
    
    @staticmethod
    def calculate_eqi(dimension_scores: List[DimensionScore]) -> float:
        """
        Calculate Equilibrium Quality Index (EQI).
        
        Formula: EQI = 1 - MIN(1, SUM(ABS(Ist_i - Soll_i)) / (N * MaxDiff))
        
        Args:
            dimension_scores: List of dimension scores
            
        Returns:
            EQI value between 0.0 and 1.0
        """
        if not dimension_scores or len(dimension_scores) != 8:
            return 0.0
        
        total_gap = sum(
            abs(float(score.ist_value) - float(score.soll_value))
            for score in dimension_scores
        )
        
        # N = 8 dimensions, MaxDiff = 3.0 (max possible difference)
        max_possible_gap = 8 * 3.0
        
        eqi = 1.0 - min(1.0, total_gap / max_possible_gap)
        
        return round(eqi, 3)
    
    @staticmethod
    def calculate_rgi(dimension_scores: List[DimensionScore]) -> float:
        """
        Calculate Reifegrad-Index (RGI) with dynamic weighting.
        
        Formula: RGI = SUM(Ist_i * Gewicht_i) / 4
        
        Args:
            dimension_scores: List of dimension scores with dynamic weights
            
        Returns:
            RGI value between 0.0 and 1.0
        """
        if not dimension_scores or len(dimension_scores) != 8:
            return 0.0
        
        weighted_sum = sum(
            float(score.ist_value) * float(score.dynamic_weight)
            for score in dimension_scores
        )
        
        # Divide by 4 to scale to 0-1 range (since max ist_value is 4.0)
        rgi = weighted_sum / 4.0
        
        return round(rgi, 3)
    
    @staticmethod
    def calculate_si(dimension_scores: List[DimensionScore]) -> float:
        """
        Calculate Spannungsindex (SI) based on critical dimension pairs.
        
        Formula: SI = SUM(ABS(Spannung_i) * Gewicht_Paar_i) / MaxSpannung
        
        Args:
            dimension_scores: List of dimension scores
            
        Returns:
            SI value between 0.0 and 1.0
        """
        if not dimension_scores or len(dimension_scores) != 8:
            return 0.0
        
        # Create lookup dict for dimension scores
        scores_dict = {
            score.dimension_id: score for score in dimension_scores
        }
        
        total_tension = 0.0
        pair_weight = 1.0 / len(AIHECalculationEngine.TENSION_PAIRS)  # Equal weighting
        
        for dim_a, dim_b in AIHECalculationEngine.TENSION_PAIRS:
            if dim_a in scores_dict and dim_b in scores_dict:
                score_a = scores_dict[dim_a]
                score_b = scores_dict[dim_b]
                
                # Calculate gap from target for each dimension
                gap_a = float(score_a.ist_value) - float(score_a.soll_value)
                gap_b = float(score_b.ist_value) - float(score_b.soll_value)
                
                # Calculate tension between the pair
                tension = abs(gap_a - gap_b)
                total_tension += tension * pair_weight
        
        # MaxSpannung = 6.0 (maximum theoretical tension)
        si = total_tension / 6.0
        
        return round(min(si, 1.0), 3)
    
    @staticmethod
    def calculate_sbs(eqi: float, si: float, rgi: float) -> float:
        """
        Calculate System Balance Score (SBS).
        
        Formula: SBS = (EQI + (1 - SI) + RGI) / 3
        
        Args:
            eqi: Equilibrium Quality Index
            si: Spannungsindex
            rgi: Reifegrad-Index
            
        Returns:
            SBS value between 0.0 and 1.0
        """
        sbs = (eqi + (1.0 - si) + rgi) / 3.0
        return round(sbs, 3)
    
    @staticmethod
    def calculate_context_score(context_factors: List[ContextFactor]) -> float:
        """
        Calculate Context Score based on organizational complexity factors.
        
        The context score quantifies the complexity of the organizational environment
        based on 8 context factors, each rated 0-3.
        
        Args:
            context_factors: List of context factors with values 0-3
            
        Returns:
            Context score between 0.0 and 1.0
        """
        if not context_factors:
            return 0.5  # Default neutral score
        
        # Expected context factors (as per specification)
        expected_factors = [
            "Organisationsgröße",
            "Branchendynamik", 
            "Regulatorischer Druck",
            "Technologische Komplexität",
            "Change-Historie",
            "Marktdynamik",
            "Wettbewerbsdruck",
            "Ressourcenverfügbarkeit"
        ]
        
        factor_values = {}
        for factor in context_factors:
            factor_values[factor.factor_name] = factor.factor_value
        
        total_score = 0
        for factor_name in expected_factors:
            value = factor_values.get(factor_name, 1)  # Default to 1 if missing
            
            # Special handling for "Ressourcenverfügbarkeit" (inverted scale)
            if factor_name == "Ressourcenverfügbarkeit":
                value = 3 - value  # Invert the scale
            
            total_score += value
        
        # Normalize to 0-1 scale (max possible score is 8 * 3 = 24)
        context_score = total_score / 24.0
        
        return round(context_score, 3)
    
    @classmethod
    def calculate_all_metrics(
        cls,
        dimension_scores: List[DimensionScore],
        context_factors: List[ContextFactor]
    ) -> Dict[str, float]:
        """
        Calculate all core metrics for an assessment.
        
        Args:
            dimension_scores: List of dimension scores
            context_factors: List of context factors
            
        Returns:
            Dictionary with all calculated metrics
        """
        eqi = cls.calculate_eqi(dimension_scores)
        rgi = cls.calculate_rgi(dimension_scores)
        si = cls.calculate_si(dimension_scores)
        sbs = cls.calculate_sbs(eqi, si, rgi)
        context_score = cls.calculate_context_score(context_factors)
        
        return {
            "eqi": eqi,
            "rgi": rgi,
            "si": si,
            "sbs": sbs,
            "context_score": context_score
        }


class DynamicWeightingEngine:
    """
    Engine for calculating dynamic weights based on context and archetype.
    
    This engine adjusts dimension weights based on organizational context
    and archetype to provide more accurate assessments.
    """
    
    # Base weights for different archetypes
    ARCHETYPE_WEIGHTS = {
        "CHAOTIC_DOER": {
            "D1": 0.20,  # Higher focus on governance
            "D2": 0.18,  # Higher focus on strategy
            "D3": 0.10,  # Lower - culture often chaotic
            "D4": 0.12,  # Moderate competence focus
            "D5": 0.12,  # Moderate data focus
            "D6": 0.08,  # Lower - tech often already strong
            "D7": 0.10,  # Lower - processes often weak
            "D8": 0.10,  # Lower - impact measurement weak
        },
        "CAUTIOUS_CORPORATE": {
            "D1": 0.15,  # Moderate governance (already strong)
            "D2": 0.15,  # Moderate strategy focus
            "D3": 0.15,  # Higher culture focus (change resistance)
            "D4": 0.15,  # Higher competence focus
            "D5": 0.10,  # Lower data focus (often good)
            "D6": 0.12,  # Moderate tech focus
            "D7": 0.08,  # Lower process focus (often good)
            "D8": 0.10,  # Moderate impact focus
        },
        "STAGNANT_ESTABLISHED": {
            "D1": 0.12,  # Moderate governance
            "D2": 0.18,  # Higher strategy focus (need direction)
            "D3": 0.18,  # Higher culture focus (change needed)
            "D4": 0.15,  # Higher competence focus
            "D5": 0.10,  # Moderate data focus
            "D6": 0.15,  # Higher tech focus (modernization)
            "D7": 0.07,  # Lower process focus
            "D8": 0.05,  # Lower impact focus
        },
        "BALANCED_TRANSFORMER": {
            "D1": 0.125,  # Balanced approach
            "D2": 0.125,
            "D3": 0.125,
            "D4": 0.125,
            "D5": 0.125,
            "D6": 0.125,
            "D7": 0.125,
            "D8": 0.125,
        }
    }
    
    @classmethod
    def calculate_dynamic_weights(
        cls,
        archetype: str,
        context_score: float,
        dimension_scores: List[DimensionScore] = None
    ) -> Dict[str, float]:
        """
        Calculate dynamic weights for dimensions based on archetype and context.
        
        Args:
            archetype: Organization archetype
            context_score: Calculated context score
            dimension_scores: Current dimension scores (optional)
            
        Returns:
            Dictionary with dynamic weights for each dimension
        """
        # Start with base archetype weights
        base_weights = cls.ARCHETYPE_WEIGHTS.get(
            archetype, 
            cls.ARCHETYPE_WEIGHTS["BALANCED_TRANSFORMER"]
        )
        
        # Apply context adjustments
        adjusted_weights = {}
        context_factor = 1.0 + (context_score - 0.5) * 0.2  # ±10% adjustment
        
        for dim_id, weight in base_weights.items():
            adjusted_weights[dim_id] = weight * context_factor
        
        # Normalize weights to sum to 1.0
        total_weight = sum(adjusted_weights.values())
        normalized_weights = {
            dim_id: weight / total_weight
            for dim_id, weight in adjusted_weights.items()
        }
        
        # Round to 3 decimal places
        return {
            dim_id: round(weight, 3)
            for dim_id, weight in normalized_weights.items()
        }


class GapAnalysisEngine:
    """
    Engine for analyzing gaps and calculating priorities.
    
    This engine identifies critical gaps and calculates priority levels
    for subdimensions based on the assessment results.
    """
    
    @staticmethod
    def calculate_subdimension_gap(ist_value: float, soll_value: float) -> Tuple[float, float]:
        """
        Calculate gap and gap percentage for a subdimension.
        
        Args:
            ist_value: Current maturity level (1.0-4.0)
            soll_value: Target maturity level (1.0-4.0)
            
        Returns:
            Tuple of (gap, gap_percentage)
        """
        gap = abs(soll_value - ist_value)
        gap_percentage = (gap / 4.0) * 100.0
        
        return round(gap, 1), round(gap_percentage, 2)
    
    @staticmethod
    def calculate_priority_level(ist_value: float, gap: float) -> str:
        """
        Calculate priority level based on current value and gap.
        
        Logic from specification:
        - IF ist_value < 2.0 AND gap > 1.5 THEN priority = CRITICAL
        - ELSE IF ist_value < 2.5 AND gap > 1.0 THEN priority = HIGH
        - ELSE IF gap > 1.5 THEN priority = HIGH
        - ELSE IF gap > 0.8 THEN priority = MEDIUM
        - ELSE priority = LOW
        
        Args:
            ist_value: Current maturity level
            gap: Gap to target
            
        Returns:
            Priority level string
        """
        if ist_value < 2.0 and gap > 1.5:
            return "CRITICAL"
        elif ist_value < 2.5 and gap > 1.0:
            return "HIGH"
        elif gap > 1.5:
            return "HIGH"
        elif gap > 0.8:
            return "MEDIUM"
        else:
            return "LOW"
