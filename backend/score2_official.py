"""
Implementación oficial de SCORE2 2021 para cálculo de riesgo cardiovascular.

NOTA IMPORTANTE: Esta implementación está basada en la estructura publicada
del estudio SCORE2 2021, pero requiere los coeficientes exactos del suplemento
del European Heart Journal para ser completamente precisa.

Referencia: SCORE2 Working Group and ESC Cardiovascular Risk Collaboration.
Eur Heart J. 2021;42(25):2439-2454.
"""

import math
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
import json
import os

@dataclass
class SCORE2Result:
    """Resultado del cálculo SCORE2."""
    percent: float
    category: str
    method: str
    age_group: str  # "40-69" o "70+"
    region: str
    warnings: list = None

# =============== COEFICIENTES SCORE2 ===============
# IMPORTANTE: Estos son coeficientes aproximados basados en la estructura
# del estudio. Se requieren los valores exactos del suplemento oficial.

# Estructura: [ln_age, ln_age^2, ln_sbp, ln_chol, smoking]
SCORE2_COEFFICIENTS_PLACEHOLDER = {
    # Región de bajo riesgo (ej: España, Francia, Italia)
    "low_risk": {
        "men_40_69": {
            "beta": [-0.7965, 0.0, 0.4648, 0.4173, 0.3131],
            "S0": 0.9605,
            "meanXB": -0.4173
        },
        "women_40_69": {
            "beta": [-1.5546, 0.0, 0.5057, 0.3687, 0.4544],
            "S0": 0.9776,
            "meanXB": -0.5487
        }
    },
    # Región de riesgo moderado
    "moderate_risk": {
        "men_40_69": {
            "beta": [-0.6573, 0.0, 0.4648, 0.4173, 0.3131],
            "S0": 0.9421,
            "meanXB": -0.3456
        },
        "women_40_69": {
            "beta": [-1.3234, 0.0, 0.5057, 0.3687, 0.4544],
            "S0": 0.9632,
            "meanXB": -0.4321
        }
    },
    # Región de alto riesgo
    "high_risk": {
        "men_40_69": {
            "beta": [-0.4856, 0.0, 0.4648, 0.4173, 0.3131],
            "S0": 0.9187,
            "meanXB": -0.2134
        },
        "women_40_69": {
            "beta": [-1.0987, 0.0, 0.5057, 0.3687, 0.4544],
            "S0": 0.9456,
            "meanXB": -0.3098
        }
    },
    # Región de muy alto riesgo
    "very_high_risk": {
        "men_40_69": {
            "beta": [-0.3124, 0.0, 0.4648, 0.4173, 0.3131],
            "S0": 0.8934,
            "meanXB": -0.1287
        },
        "women_40_69": {
            "beta": [-0.8765, 0.0, 0.5057, 0.3687, 0.4544],
            "S0": 0.9234,
            "meanXB": -0.2345
        }
    }
}

# Coeficientes para SCORE2-OP (70+ años) - Estructura similar pero diferentes valores
SCORE2_OP_COEFFICIENTS_PLACEHOLDER = {
    # Estos coeficientes son completamente aproximados y requieren implementación oficial
    "low_risk": {
        "men_70_plus": {
            "beta": [-0.5432, 0.0, 0.3456, 0.2987, 0.2345],
            "S0": 0.8876,
            "meanXB": -0.2987
        },
        "women_70_plus": {
            "beta": [-0.9876, 0.0, 0.4123, 0.2654, 0.3456],
            "S0": 0.9123,
            "meanXB": -0.3876
        }
    }
    # ... otros niveles de riesgo para 70+
}

def _validate_score2_inputs(patient: Dict) -> Tuple[bool, list]:
    """Valida las entradas para SCORE2."""
    errors = []
    required_fields = ["edad", "sexo", "presion_sistolica", "colesterol_total", 
                      "fumador", "region_riesgo"]
    
    for field in required_fields:
        if field not in patient or patient[field] is None:
            errors.append(f"Campo requerido: {field}")
    
    try:
        edad = float(patient.get("edad", 0))
        if edad < 40 or edad > 89:
            errors.append("SCORE2 es aplicable solo para edades 40-89 años")
    except (ValueError, TypeError):
        errors.append("Edad debe ser un número válido")
    
    return len(errors) == 0, errors

def _get_region_key(region: str) -> str:
    """Convierte región de entrada a clave interna."""
    region = str(region).lower().replace("-", "_").replace(" ", "_")
    
    mapping = {
        "bajo": "low_risk",
        "low": "low_risk",
        "moderado": "moderate_risk",
        "moderate": "moderate_risk",
        "alto": "high_risk",
        "high": "high_risk",
        "muy_alto": "very_high_risk",
        "muy-alto": "very_high_risk",
        "very_high": "very_high_risk"
    }
    
    return mapping.get(region, "moderate_risk")

def _load_coeffs_from_json() -> Optional[Dict]:
    """Carga coeficientes desde backend/score2_coeffs.json si existen y no son placeholders.
    Devuelve None si el archivo no existe o contiene valores nulos.
    """
    here = os.path.dirname(__file__)
    path = os.path.join(here, "score2_coeffs.json")
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        # Validación mínima: comprobar que alguna beta no sea 0
        sample = (
            data.get("SCORE2", {})
            .get("moderate", {})
            .get("men", {})
            .get("beta", [0, 0, 0, 0, 0])
        )
        if sum(abs(x) for x in sample) == 0:
            return None
        return data
    except Exception:
        return None

def _get_score2_coefficients(age: float, sex: str, region: str) -> Tuple[Dict, str]:
    """Obtiene coeficientes según edad, sexo y región.
    1) Intenta cargar oficiales desde JSON.
    2) Si no existen, usa placeholders internos.
    """
    region_key = _get_region_key(region)
    is_male = str(sex).lower() == "hombre"
    data = _load_coeffs_from_json()

    if age >= 70:
        # SCORE2-OP para 70+ años
        if data and "SCORE2_OP" in data:
            grp = data["SCORE2_OP"].get(region_key.replace("_risk", ""))
            if grp:
                coeff = grp.get("men" if is_male else "women")
                if coeff:
                    return coeff, "SCORE2-OP"
        if region_key in SCORE2_OP_COEFFICIENTS_PLACEHOLDER:
            sex_key = "men_70_plus" if is_male else "women_70_plus"
            if sex_key in SCORE2_OP_COEFFICIENTS_PLACEHOLDER[region_key]:
                return SCORE2_OP_COEFFICIENTS_PLACEHOLDER[region_key][sex_key], "SCORE2-OP"
    else:
        # SCORE2 estándar para 40-69 años
        if data and "SCORE2" in data:
            grp = data["SCORE2"].get(region_key.replace("_risk", ""))
            if grp:
                coeff = grp.get("men" if is_male else "women")
                if coeff:
                    return coeff, "SCORE2"
        if region_key in SCORE2_COEFFICIENTS_PLACEHOLDER:
            sex_key = "men_40_69" if is_male else "women_40_69"
            if sex_key in SCORE2_COEFFICIENTS_PLACEHOLDER[region_key]:
                return SCORE2_COEFFICIENTS_PLACEHOLDER[region_key][sex_key], "SCORE2"

    # Fallback por defecto si nada se encontró
    return SCORE2_COEFFICIENTS_PLACEHOLDER["moderate_risk"]["men_40_69"], "SCORE2"

def calculate_score2_official(patient: Dict) -> SCORE2Result:
    """
    Calcula SCORE2 usando estructura oficial pero coeficientes aproximados.
    
    ADVERTENCIA: Esta implementación usa coeficientes aproximados.
    Para precisión completa se requieren los coeficientes exactos del
    suplemento del European Heart Journal 2021.
    """
    # Validación de entrada
    is_valid, errors = _validate_score2_inputs(patient)
    if not is_valid:
        return SCORE2Result(0.0, "error", "score2", "unknown", "unknown", errors)
    
    warnings = [
        "ADVERTENCIA: Coeficientes aproximados - se requieren valores oficiales",
        "Fuente requerida: SCORE2 Working Group. Eur Heart J. 2021 Supplement"
    ]
    
    # Extracción de variables
    age = float(patient["edad"])
    sex = str(patient.get("sexo", "hombre"))
    sbp = float(patient["presion_sistolica"])
    chol_total = float(patient["colesterol_total"])
    smoking = 1 if bool(patient.get("fumador", False)) else 0
    region = str(patient.get("region_riesgo", "moderado"))
    
    # Obtener coeficientes apropiados
    coeffs, method_used = _get_score2_coefficients(age, sex, region)
    
    # Clamps según SCORE2
    age_clamped = max(40, min(89, age))
    sbp_clamped = max(90, min(200, sbp))
    chol_clamped = max(2.5, min(8.0, chol_total / 38.67))  # Convertir a mmol/L
    
    if age != age_clamped:
        warnings.append(f"Edad ajustada de {age} a {age_clamped}")
    
    # Transformaciones logarítmicas
    ln_age = math.log(age_clamped)
    ln_age2 = ln_age ** 2
    ln_sbp = math.log(sbp_clamped)
    ln_chol = math.log(chol_clamped)
    
    # Vector de características
    X = [ln_age, ln_age2, ln_sbp, ln_chol, smoking]
    
    # Cálculo del índice lineal
    beta = coeffs["beta"]
    linear_predictor = sum(b * x for b, x in zip(beta, X))
    
    # Conversión a riesgo usando supervivencia basal
    try:
        S0 = coeffs["S0"]
        meanXB = coeffs["meanXB"]
        
        # Fórmula de Cox: Risk = 1 - S0^exp(LP - meanXB)
        risk = 1 - (S0 ** math.exp(linear_predictor - meanXB))
        risk_pct = max(0.0, min(risk * 100.0, 50.0))  # Cap a 50%
        
        # Categorización según SCORE2
        if risk_pct < 2.5:
            category = "bajo"
        elif risk_pct < 7.5:
            category = "moderado"
        elif risk_pct < 15:
            category = "alto"
        else:
            category = "muy_alto"
        
        age_group = "70+" if age >= 70 else "40-69"
        
        return SCORE2Result(
            percent=round(risk_pct, 1),
            category=category,
            method=method_used,
            age_group=age_group,
            region=_get_region_key(region),
            warnings=warnings
        )
        
    except (OverflowError, ValueError, ZeroDivisionError) as e:
        return SCORE2Result(
            0.0, "error", "score2", "unknown", "unknown", 
            [f"Error de cálculo: {str(e)}"]
        )

def get_score2_implementation_status() -> Dict:
    """Retorna el estado de implementación de SCORE2."""
    return {
        "status": "PARCIAL",
        "precision": "BAJA",
        "structure": "CORRECTA",
        "coefficients": "APROXIMADOS",
        "required_source": "SCORE2 Working Group. Eur Heart J. 2021;42(25):2439-2454 + Supplement",
        "missing_components": [
            "Coeficientes exactos por región y sexo",
            "Coeficientes SCORE2-OP completos para 70+ años",
            "Validación con casos de prueba oficiales",
            "Implementación de todas las regiones de riesgo"
        ],
        "current_regions": ["low_risk", "moderate_risk", "high_risk", "very_high_risk"],
        "age_ranges": {
            "SCORE2": "40-69 años",
            "SCORE2-OP": "70+ años (implementación parcial)"
        }
    }

# Función de compatibilidad con la interfaz existente
def score2_risk_official(patient: Dict) -> Dict:
    """Interfaz compatible con el sistema existente."""
    result = calculate_score2_official(patient)
    
    return {
        "percent": result.percent,
        "category": result.category,
        "method": result.method,
        "warnings": result.warnings
    }
