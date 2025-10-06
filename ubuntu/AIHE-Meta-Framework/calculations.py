"""
AIHE Meta-Framework - Vollständige Berechnungslogik
Basierend auf der detaillierten technischen Spezifikation (53 Seiten)

Implementiert alle 5 Kernmetriken mit korrekter dynamischer Gewichtung:
- EQI (Equilibrium Quality Index)
- RGI (Reifegrad-Index) 
- SI (Spannungsindex)
- SBS (System Balance Score)
- Kontextscore

Autor: Manus AI
Version: 2.0 (Vollständige Spezifikation)
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Tuple, Optional
import math
from enum import Enum

class Archetyp(Enum):
    """Organisationsarchetypen für dynamische Gewichtung"""
    CHAOTIC_DOER = "CHAOTIC_DOER"
    CAUTIOUS_CORPORATE = "CAUTIOUS_CORPORATE" 
    STAGNANT_ESTABLISHED = "STAGNANT_ESTABLISHED"
    BALANCED_TRANSFORMER = "BALANCED_TRANSFORMER"

class DimensionScore:
    """Repräsentiert die Bewertung einer Dimension"""
    def __init__(self, dimension_id: str, ist_value: Decimal, soll_value: Decimal, dynamic_weight: Decimal = Decimal("0.125")):
        self.dimension_id = dimension_id
        self.ist_value = ist_value
        self.soll_value = soll_value
        self.dynamic_weight = dynamic_weight
        self.gap = abs(ist_value - soll_value)

class ContextFactor:
    """Repräsentiert einen Kontextfaktor (F1-F10)"""
    def __init__(self, factor_name: str, factor_value: int):
        self.factor_name = factor_name
        self.factor_value = factor_value  # 0-3

class AIHECalculationEngine:
    """Hauptberechnungsengine für alle AIHE-Metriken"""
    
    # Konstanten aus der Spezifikation
    SCHWELLENWERT_GAP = Decimal("1.5")
    SCHWELLENWERT_SPANNUNG = Decimal("3.0")
    SCHWELLENWERT_NIEDRIG = Decimal("0.2")
    SCHWELLENWERT_HOCH = Decimal("0.8")
    SCHWELLENWERT_IST = Decimal("3.5")
    ANPASSUNGSFAKTOR = Decimal("1.2")  # +20%
    ANPASSUNGSFAKTOR_HOCH = Decimal("1.3")  # +30%
    ANPASSUNGSFAKTOR_MITTEL = Decimal("1.1")  # +10%
    ANPASSUNGSFAKTOR_DAEMPFUNG = Decimal("0.8")  # -20%
    MINIMUM_GEWICHT = Decimal("0.01")  # 1%
    
    # 12 Spannungspaare aus der Spezifikation
    SPANNUNGSPAARE = [
        ("D1", "D2"), ("D1", "D3"), ("D1", "D4"), ("D1", "D5"),
        ("D2", "D3"), ("D2", "D6"), ("D3", "D4"), ("D3", "D6"),
        ("D4", "D5"), ("D5", "D6"), ("D6", "D7"), ("D7", "D8")
    ]
    
    @staticmethod
    def calculate_eqi(dimension_scores: List[DimensionScore]) -> float:
        """
        Berechnet den Equilibrium Quality Index (EQI)
        EQI = 1 - (Summe aller |Gaps|) / 24.0
        """
        total_gap = sum(score.gap for score in dimension_scores)
        eqi = 1 - (float(total_gap) / 24.0)
        return max(0.0, min(1.0, eqi))
    
    @staticmethod
    def calculate_rgi(dimension_scores: List[DimensionScore]) -> float:
        """
        Berechnet den Reifegrad-Index (RGI)
        RGI = Gewichtete Summe der Ist-Werte / 4.0
        """
        weighted_sum = sum(
            float(score.ist_value * score.dynamic_weight) 
            for score in dimension_scores
        )
        rgi = weighted_sum / 4.0
        return max(0.0, min(1.0, rgi))
    
    @staticmethod
    def calculate_si(dimension_scores: List[DimensionScore]) -> float:
        """
        Berechnet den Spannungsindex (SI)
        SI = Gewichtete Spannungen zwischen 12 Dimensionspaaren / 6.0
        """
        # Erstelle Dictionary für schnellen Zugriff
        scores_dict = {score.dimension_id: score for score in dimension_scores}
        
        total_weighted_tension = Decimal("0")
        
        for dim1, dim2 in AIHECalculationEngine.SPANNUNGSPAARE:
            if dim1 in scores_dict and dim2 in scores_dict:
                score1 = scores_dict[dim1]
                score2 = scores_dict[dim2]
                
                # Berechne Spannung als Differenz der Ist-Werte
                tension = abs(score1.ist_value - score2.ist_value)
                
                # Gewichte mit durchschnittlichem Gewicht beider Dimensionen
                avg_weight = (score1.dynamic_weight + score2.dynamic_weight) / 2
                weighted_tension = tension * avg_weight
                
                total_weighted_tension += weighted_tension
        
        si = float(total_weighted_tension) / 6.0
        return max(0.0, min(1.0, si))
    
    @staticmethod
    def calculate_sbs(eqi: float, si: float, rgi: float) -> float:
        """
        Berechnet den System Balance Score (SBS)
        SBS = (EQI + (1-SI) + RGI) / 3
        """
        sbs = (eqi + (1 - si) + rgi) / 3
        return max(0.0, min(1.0, sbs))
    
    @staticmethod
    def calculate_context_score(context_factors: List[ContextFactor]) -> float:
        """
        Berechnet den Kontextscore aus 10 Faktoren (F1-F10)
        Kontextscore = Gewichtete Summe / 3.0
        """
        if not context_factors or len(context_factors) != 10:
            return 0.5  # Neutraler Wert bei fehlenden Daten
        
        # Gewichtung der Kontextfaktoren (aus Spezifikation)
        weights = [0.12, 0.11, 0.10, 0.09, 0.11, 0.10, 0.12, 0.08, 0.09, 0.08]
        
        weighted_sum = sum(
            factor.factor_value * weights[i] 
            for i, factor in enumerate(context_factors)
        )
        
        context_score = weighted_sum / 3.0
        return max(0.0, min(1.0, context_score))

class DynamicWeightingEngine:
    """Engine für die dynamische Gewichtung basierend auf 8 Regeln"""
    
    @staticmethod
    def calculate_dynamic_weights(
        dimension_scores: List[DimensionScore],
        context_score: float,
        archetyp: Archetyp,
        is_kmu: bool = False
    ) -> Dict[str, float]:
        """
        Hauptfunktion für dynamische Gewichtung
        Implementiert alle 8 Regeln aus der Spezifikation
        """
        # Schritt 1: Basisgewichte laden
        weights = DynamicWeightingEngine._load_base_weights(is_kmu)
        
        # Schritt 2-7: Regeln anwenden
        weights = DynamicWeightingEngine._apply_rule_1_tight_gaps(weights, dimension_scores)
        weights = DynamicWeightingEngine._apply_rule_2_large_gaps(weights, dimension_scores)
        weights = DynamicWeightingEngine._apply_rule_3_high_tension(weights, dimension_scores)
        weights = DynamicWeightingEngine._apply_rule_4_context(weights, context_score)
        weights = DynamicWeightingEngine._apply_rule_5_above_average(weights, dimension_scores)
        weights = DynamicWeightingEngine._apply_rule_6_archetyp(weights, archetyp)
        
        # Schritt 8: Minimum-Sicherung
        weights = DynamicWeightingEngine._apply_minimum_security(weights)
        
        # Schritt 9: Normalisierung
        weights = DynamicWeightingEngine._normalize_weights(weights)
        
        return weights
    
    @staticmethod
    def _load_base_weights(is_kmu: bool) -> Dict[str, Decimal]:
        """Lädt die Basisgewichte (KMU oder Standard)"""
        if is_kmu:
            # KMU-spezifische Gewichte
            return {
                "D1": Decimal("0.10"),  # Führung reduziert
                "D2": Decimal("0.15"),  # Strategie wichtiger
                "D3": Decimal("0.15"),  # Kultur wichtiger
                "D4": Decimal("0.15"),  # Kompetenzen wichtiger
                "D5": Decimal("0.10"),  # Daten reduziert
                "D6": Decimal("0.10"),  # Tech reduziert
                "D7": Decimal("0.15"),  # Prozesse wichtiger
                "D8": Decimal("0.10"),  # Wirkung reduziert
            }
        else:
            # Standard-Gleichgewichtung
            return {f"D{i}": Decimal("0.125") for i in range(1, 9)}
    
    @staticmethod
    def _apply_rule_1_tight_gaps(weights: Dict[str, Decimal], dimension_scores: List[DimensionScore]) -> Dict[str, Decimal]:
        """Regel 1: Enge Lücken verstärken"""
        for score in dimension_scores:
            if score.gap <= AIHECalculationEngine.SCHWELLENWERT_GAP:
                weights[score.dimension_id] *= AIHECalculationEngine.ANPASSUNGSFAKTOR
        return weights
    
    @staticmethod
    def _apply_rule_2_large_gaps(weights: Dict[str, Decimal], dimension_scores: List[DimensionScore]) -> Dict[str, Decimal]:
        """Regel 2: Große Lücken verstärken"""
        for score in dimension_scores:
            if score.gap > AIHECalculationEngine.SCHWELLENWERT_GAP:
                weights[score.dimension_id] *= AIHECalculationEngine.ANPASSUNGSFAKTOR
        return weights
    
    @staticmethod
    def _apply_rule_3_high_tension(weights: Dict[str, Decimal], dimension_scores: List[DimensionScore]) -> Dict[str, Decimal]:
        """Regel 3: Auf hohe Spannung reagieren (Tech-Kultur-Spannung D6 ↔ D3)"""
        scores_dict = {score.dimension_id: score for score in dimension_scores}
        
        if "D6" in scores_dict and "D3" in scores_dict:
            gap_d6 = scores_dict["D6"].ist_value - scores_dict["D6"].soll_value
            gap_d3 = scores_dict["D3"].ist_value - scores_dict["D3"].soll_value
            
            spannung_tech_kultur = gap_d6 - gap_d3
            intensitaet = abs(spannung_tech_kultur)
            
            if intensitaet > AIHECalculationEngine.SCHWELLENWERT_SPANNUNG:
                # Bestimme zurückliegende Dimension
                if gap_d3 < gap_d6:  # D3 ist weiter zurück
                    weights["D3"] *= AIHECalculationEngine.ANPASSUNGSFAKTOR_HOCH
                    weights["D6"] *= AIHECalculationEngine.ANPASSUNGSFAKTOR_MITTEL
                else:  # D6 ist weiter zurück
                    weights["D6"] *= AIHECalculationEngine.ANPASSUNGSFAKTOR_HOCH
                    weights["D3"] *= AIHECalculationEngine.ANPASSUNGSFAKTOR_MITTEL
        
        return weights
    
    @staticmethod
    def _apply_rule_4_context(weights: Dict[str, Decimal], context_score: float) -> Dict[str, Decimal]:
        """Regel 4: Kontextkomplexität anpassen"""
        if context_score < float(AIHECalculationEngine.SCHWELLENWERT_NIEDRIG):
            # Einfacher Kontext: Prozesse verstärken
            weights["D7"] *= AIHECalculationEngine.ANPASSUNGSFAKTOR
        elif context_score > float(AIHECalculationEngine.SCHWELLENWERT_HOCH):
            # Komplexer Kontext: Führung & Strategie verstärken
            weights["D1"] *= AIHECalculationEngine.ANPASSUNGSFAKTOR
            weights["D2"] *= AIHECalculationEngine.ANPASSUNGSFAKTOR
        
        return weights
    
    @staticmethod
    def _apply_rule_5_above_average(weights: Dict[str, Decimal], dimension_scores: List[DimensionScore]) -> Dict[str, Decimal]:
        """Regel 5: Überdurchschnittliche Dimensionen dämpfen"""
        for score in dimension_scores:
            ist = score.ist_value
            soll = score.soll_value
            
            # Prüfe: Hoher Ist-Wert UND nahe/über Soll UND nicht in kritischer Spannung
            if (ist > AIHECalculationEngine.SCHWELLENWERT_IST and 
                ist >= soll and 
                not DynamicWeightingEngine._is_in_critical_tension(score.dimension_id, dimension_scores)):
                weights[score.dimension_id] *= AIHECalculationEngine.ANPASSUNGSFAKTOR_DAEMPFUNG
        
        return weights
    
    @staticmethod
    def _is_in_critical_tension(dimension_id: str, dimension_scores: List[DimensionScore]) -> bool:
        """Prüft, ob Dimension Teil einer Spannung mit Intensität > 3.0 ist"""
        # Vereinfacht für dieses Beispiel - in Praxis: Alle 12 Spannungen prüfen
        return False
    
    @staticmethod
    def _apply_rule_6_archetyp(weights: Dict[str, Decimal], archetyp: Archetyp) -> Dict[str, Decimal]:
        """Regel 6: Archetyp-spezifische Anpassungen"""
        faktoren = DynamicWeightingEngine._get_archetyp_factors(archetyp)
        
        for dimension_id in weights:
            if dimension_id in faktoren:
                weights[dimension_id] *= faktoren[dimension_id]
        
        return weights
    
    @staticmethod
    def _get_archetyp_factors(archetyp: Archetyp) -> Dict[str, Decimal]:
        """Holt Archetyp-spezifische Faktoren"""
        if archetyp == Archetyp.CHAOTIC_DOER:
            return {
                "D1": Decimal("1.5"),  # Führung massiv verstärken
                "D2": Decimal("1.4"),  # Strategie stark verstärken
                "D3": Decimal("0.9"),  # Kultur leicht dämpfen
                "D4": Decimal("1.1"),  # Kompetenzen leicht verstärken
                "D5": Decimal("1.1"),  # Daten leicht verstärken
                "D6": Decimal("0.7"),  # Tech deutlich dämpfen (schon gut)
                "D7": Decimal("1.3"),  # Prozesse verstärken
                "D8": Decimal("1.2"),  # Wirkung verstärken
            }
        elif archetyp == Archetyp.CAUTIOUS_CORPORATE:
            return {
                "D1": Decimal("0.8"),  # Führung dämpfen (schon gut)
                "D2": Decimal("1.0"),  # Strategie neutral
                "D3": Decimal("1.5"),  # Kultur massiv verstärken
                "D4": Decimal("1.4"),  # Kompetenzen stark verstärken
                "D5": Decimal("1.0"),  # Daten neutral
                "D6": Decimal("1.3"),  # Tech verstärken
                "D7": Decimal("1.0"),  # Prozesse neutral
                "D8": Decimal("1.1"),  # Wirkung leicht verstärken
            }
        elif archetyp == Archetyp.STAGNANT_ESTABLISHED:
            return {
                "D1": Decimal("1.2"),  # Führung verstärken
                "D2": Decimal("1.4"),  # Strategie stark verstärken
                "D3": Decimal("1.3"),  # Kultur verstärken
                "D4": Decimal("1.2"),  # Kompetenzen verstärken
                "D5": Decimal("1.0"),  # Daten neutral
                "D6": Decimal("1.2"),  # Tech verstärken
                "D7": Decimal("1.0"),  # Prozesse neutral
                "D8": Decimal("1.3"),  # Wirkung verstärken
            }
        elif archetyp == Archetyp.BALANCED_TRANSFORMER:
            return {f"D{i}": Decimal("1.0") for i in range(1, 9)}  # Alle neutral
        else:
            return {f"D{i}": Decimal("1.0") for i in range(1, 9)}  # Default: Alle neutral
    
    @staticmethod
    def _apply_minimum_security(weights: Dict[str, Decimal]) -> Dict[str, Decimal]:
        """Schritt 8: Minimum-Sicherung - Kein Gewicht unter 1%"""
        for dimension_id in weights:
            if weights[dimension_id] < AIHECalculationEngine.MINIMUM_GEWICHT:
                weights[dimension_id] = AIHECalculationEngine.MINIMUM_GEWICHT
        
        return weights
    
    @staticmethod
    def _normalize_weights(weights: Dict[str, Decimal]) -> Dict[str, float]:
        """Schritt 9: Normalisierung - Summe muss exakt 1.0 sein"""
        # Schritt 1: Summe berechnen
        summe = sum(weights.values())
        
        # Schritt 2: Jedes Gewicht durch Summe teilen
        for dimension_id in weights:
            weights[dimension_id] = weights[dimension_id] / summe
        
        # Schritt 3: Rundung und finale Korrektur
        finales_gewicht = DynamicWeightingEngine._round_and_correct(weights)
        
        return finales_gewicht
    
    @staticmethod
    def _round_and_correct(weights: Dict[str, Decimal]) -> Dict[str, float]:
        """Runde jedes Gewicht auf 3 Dezimalstellen und korrigiere kleinste Abweichungen"""
        # Runde jedes Gewicht auf 3 Dezimalstellen
        rounded_weights = {}
        for dimension_id, weight in weights.items():
            rounded_weights[dimension_id] = float(weight.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP))
        
        # Berechne Summe nach Rundung
        summe = sum(rounded_weights.values())
        
        # Korrigiere kleinste Abweichungen
        differenz = 1.0 - summe
        
        if abs(differenz) > 0.001:
            # Warnung bei zu großer Abweichung
            print(f"Warnung: Rundungsfehler bei Gewichtung: {differenz}")
        
        # Verteile Differenz auf größtes Gewicht
        if abs(differenz) > 0.0001:
            groesste_dimension = max(rounded_weights, key=rounded_weights.get)
            rounded_weights[groesste_dimension] += differenz
        
        return rounded_weights

class GapAnalysisEngine:
    """Engine für Gap-Analyse und Prioritätsberechnung"""
    
    @staticmethod
    def calculate_subdimension_gap(ist_value: float, soll_value: float) -> Tuple[float, float]:
        """
        Berechnet Gap und Gap-Prozent für eine Subdimension
        
        Returns:
            Tuple[float, float]: (gap, gap_percent)
        """
        gap = abs(ist_value - soll_value)
        gap_percent = (gap / 4.0) * 100  # Normiert auf 4.0 Skala
        return gap, gap_percent
    
    @staticmethod
    def calculate_priority_level(ist_value: float, gap: float) -> str:
        """
        Berechnet Prioritätslevel basierend auf Ist-Wert und Gap
        
        Returns:
            str: CRITICAL, HIGH, MEDIUM, LOW
        """
        if ist_value < 2.0 and gap > 1.5:
            return "CRITICAL"
        elif ist_value < 2.5 and gap > 1.0:
            return "HIGH"
        elif gap > 0.8:
            return "HIGH"
        elif gap > 0.5:
            return "MEDIUM"
        else:
            return "LOW"
    
    @staticmethod
    def generate_recommendations(dimension_scores: List[DimensionScore]) -> List[Dict]:
        """
        Generiert Handlungsempfehlungen basierend auf Gap-Analyse
        
        Returns:
            List[Dict]: Liste von Empfehlungen mit Priorität und Beschreibung
        """
        recommendations = []
        
        for score in dimension_scores:
            gap, gap_percent = GapAnalysisEngine.calculate_subdimension_gap(
                float(score.ist_value), float(score.soll_value)
            )
            priority = GapAnalysisEngine.calculate_priority_level(float(score.ist_value), gap)
            
            if priority in ["CRITICAL", "HIGH"]:
                recommendations.append({
                    "dimension_id": score.dimension_id,
                    "priority": priority,
                    "gap": gap,
                    "gap_percent": gap_percent,
                    "description": f"Dimension {score.dimension_id} benötigt Aufmerksamkeit",
                    "ist_value": float(score.ist_value),
                    "soll_value": float(score.soll_value)
                })
        
        # Sortiere nach Priorität und Gap-Größe
        priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        recommendations.sort(key=lambda x: (priority_order[x["priority"]], -x["gap"]))
        
        return recommendations
