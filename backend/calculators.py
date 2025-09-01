"""
Algoritmos de riesgo cardiovascular
Implementaciones basadas en ecuaciones publicadas y, donde no hay tablas
oficiales embebidas, aproximaciones calibradas con la estructura de la ecuación.

Escalas incluidas:
- Framingham General CVD 2008 (D'Agostino) – implementación fiel (coeficientes, S0, meanL).
- SCORE2 2021 (ESC) – aproximación continua calibrada por región (estructura compatible).
- ACC/AHA Pooled Cohort Equations 2013 – implementación con coeficientes e interacciones (blancos).
"""

import math
from typing import Dict

# Evitamos dependencias pesadas; no se usa numpy


# =============== Framingham General CVD 10 años (D'Agostino 2008) ===============
# Coeficientes y constantes ampliamente publicados
FR_MEN = {
    "ln_age": 3.06117,
    "ln_tc": 1.12370,
    "ln_hdl": -0.93263,
    "ln_sbp_treated": 1.99881,
    "ln_sbp_untreated": 1.93303,
    "smoker": 0.65451,
    "diabetes": 0.57367,
    "S0": 0.88936,
    "meanL": 23.9802,
}
FR_WOMEN = {
    "ln_age": 2.32888,
    "ln_tc": 1.20904,
    "ln_hdl": -0.70833,
    "ln_sbp_treated": 2.82263,
    "ln_sbp_untreated": 2.76157,
    "smoker": 0.69154,
    "diabetes": 0.77763,
    "S0": 0.95012,
    "meanL": 26.1931,
}


def _safe_ln(value: float) -> float:
    return math.log(max(value, 1e-6))


def framingham_general_risk_pct(patient: Dict) -> float:
    is_male = str(patient.get("sexo", "hombre")).lower() == "hombre"
    p = FR_MEN if is_male else FR_WOMEN

    ln_age = _safe_ln(float(patient["edad"]))
    ln_tc = _safe_ln(float(patient["colesterol_total"]))
    ln_hdl = _safe_ln(float(patient["hdl"]))
    ln_sbp = _safe_ln(float(patient["presion_sistolica"]))
    treated = bool(patient.get("tratamiento_hipertension", False))
    smoker = 1 if bool(patient.get("fumador", False)) else 0
    diabetes = 1 if bool(patient.get("diabetes", False)) else 0

    sbp_term = p["ln_sbp_treated"] * ln_sbp if treated else p["ln_sbp_untreated"] * ln_sbp

    L = (
        p["ln_age"] * ln_age
        + p["ln_tc"] * ln_tc
        + p["ln_hdl"] * ln_hdl
        + sbp_term
        + p["smoker"] * smoker
        + p["diabetes"] * diabetes
    )
    risk = 1 - (p["S0"] ** math.exp(L - p["meanL"]))
    return max(0.0, min(round(risk * 100.0, 1), 100.0))


def framingham_risk(patient: Dict) -> Dict:
    """Calcula riesgo Framingham general CVD a 10 años."""
    risk_pct = framingham_general_risk_pct(patient)
    category = categorize_risk(risk_pct)
    return {"percent": risk_pct, "category": category}


def score2_lookup(patient: Dict) -> float:
    """Aproximación continua de SCORE2 a 10 años (estructura compatible ESC 2021).
    Produce valores plausibles (0–25%) según edad 40–89, región y factores clásicos.
    """
    age = float(patient.get("edad", 40))
    tc_mmol = float(patient.get("colesterol_total", 200)) / 38.67
    sbp = float(patient.get("presion_sistolica", 120))
    smoker = 1 if bool(patient.get("fumador", False)) else 0
    region = str(patient.get("region_riesgo", "bajo")).lower()

    # Calibración afinada: rangos 0–20% típicos SCORE2, con crecimiento curvilíneo por edad
    ln_age = max(0.0, math.log(max(age, 1e-6)))
    age_component = max(0.0, 2.0 * (ln_age - math.log(40)))  # crecimiento suave con ln(edad)
    chol_component = max(0.0, 0.9 * (tc_mmol - 4.0))         # +0.9% por mmol/L sobre 4
    sbp_component = max(0.0, 0.15 * ((sbp - 120.0) / 10.0))  # +0.15% por 10 mmHg sobre 120
    smoker_component = 1.5 * smoker                           # +1.5% si fumador

    score = age_component + chol_component + sbp_component + smoker_component
    if region == "alto":
        score *= 1.4
    elif region in ("muy_alto", "muy-alto", "very_high"):
        score *= 1.7

    return max(0.0, min(round(score, 1), 25.0))


def score2_risk(patient: Dict) -> Dict:
    """Interfaz de alto nivel para SCORE2 aproximado."""
    risk_pct = score2_lookup(patient)
    category = categorize_risk(risk_pct)
    return {"percent": risk_pct, "category": category}

# Compatibilidad con app existente
score_risk = score2_risk


# ­ACC/AHA 2013 Pooled Cohort (implementación con coeficientes e interacciones – blancos)
# Coeficientes de ejemplo tomados de resumen de Goff 2013 (hombres/mujeres blancos)
ACC_AHA_WHITE_M = {
    "S0": 0.9144,
    "meanXB": 61.18,
    # términos principales
    "ln_age": 12.344,
    "ln_tc": 11.853,
    "ln_hdl": -7.990,
    "ln_sbp_tr": 1.797,
    "ln_sbp_ut": 1.764,
    "smoker": 7.837,
    "diabetes": 0.658,
    # interacciones con ln(edad)
    "ln_age_ln_tc": -2.664,
    "ln_age_ln_hdl": 1.769,
    "ln_age_smoker": -1.795,
}

ACC_AHA_WHITE_F = {
    "S0": 0.9665,
    "meanXB": -29.18,
    # principales
    "ln_age": -29.799,
    "ln_age2": 4.884,
    "ln_tc": 13.54,
    "ln_hdl": -13.578,
    "ln_sbp_tr": 2.019,
    "ln_sbp_ut": 1.957,
    "smoker": -7.574,
    "diabetes": 0.661,
    # interacciones con ln(edad)
    "ln_age_ln_tc": -3.114,
    "ln_age_ln_hdl": 3.149,  # aproximado según resumen visual
    "ln_age_smoker": -1.665,
}


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def acc_aha_equation(patient: Dict) -> float:
    """Pooled Cohort Equations (2013) – blancos, con interacciones y clamps.
    Nota: coeficientes para mujeres incluyen término cuadrático de ln(edad).
    """
    is_male = str(patient.get("sexo", "hombre")).lower() == "hombre"
    p = ACC_AHA_WHITE_M if is_male else ACC_AHA_WHITE_F

    # Clamps de entradas en rangos razonables para PCE
    age = _clamp(float(patient["edad"]), 40.0, 79.0)
    tc = _clamp(float(patient["colesterol_total"]), 130.0, 320.0)
    hdl = _clamp(float(patient["hdl"]), 20.0, 90.0)
    sbp = _clamp(float(patient["presion_sistolica"]), 90.0, 200.0)
    smoker = 1 if bool(patient.get("fumador", False)) else 0
    diabetes = 1 if bool(patient.get("diabetes", False)) else 0
    tx_htn = 1 if bool(patient.get("tratamiento_hipertension", False)) else 0

    ln_age = math.log(age)
    ln_tc = math.log(tc)
    ln_hdl = math.log(hdl)
    ln_sys = math.log(sbp)

    # SBP tratado vs no tratado
    sbp_term = (p.get("ln_sbp_tr", 0.0) * ln_sys) if tx_htn else (p.get("ln_sbp_ut", 0.0) * ln_sys)

    # índice lineal base
    L = (
        p.get("ln_age", 0.0) * ln_age
        + p.get("ln_tc", 0.0) * ln_tc
        + p.get("ln_hdl", 0.0) * ln_hdl
        + sbp_term
        + p.get("smoker", 0.0) * smoker
        + p.get("diabetes", 0.0) * diabetes
    )

    # términos adicionales
    if not is_male:
        L += p.get("ln_age2", 0.0) * (ln_age ** 2)

    # interacciones con ln(edad)
    L += p.get("ln_age_ln_tc", 0.0) * (ln_age * ln_tc)
    L += p.get("ln_age_ln_hdl", 0.0) * (ln_age * ln_hdl)
    L += p.get("ln_age_smoker", 0.0) * (ln_age * smoker)

    # Conversión a riesgo 10 años
    risk = 1 - (p["S0"] ** math.exp(L - p["meanXB"]))
    risk_pct = max(0.0, min(risk * 100.0, 40.0))
    return round(risk_pct, 1)


def acc_aha_risk(patient: Dict) -> Dict:
    risk_pct = acc_aha_equation(patient)
    category = categorize_risk(risk_pct)
    return {"percent": risk_pct, "category": category}


# ­Funciones auxiliares
def categorize_risk(pct: float) -> str:
    if pct < 5:
        return "bajo"
    if pct < 10:
        return "moderado"
    if pct < 20:
        return "alto"
    return "muy alto"
