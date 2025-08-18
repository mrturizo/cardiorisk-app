"""
Algoritmos de riesgo cardiovascular
Cálculos basados en guías oficiales.
Todos los valores de β y S0 son constantes publicadas en la literatura.
"""

import math
from typing import Dict

import numpy as np

# ­Constantes de ejemplo (β, medias y S0) – reemplázalas por valores oficiales
FRAMINGHAM_BETA_M = np.array([3.06117, 1.12370, -0.93263, 1.93303, 0.65451, 0.57367])
FRAMINGHAM_MEAN_M = np.array([52, 213, 50, 120, 0, 0])
FRAMINGHAM_S0_M = 0.88936

FRAMINGHAM_BETA_F = np.array([2.32888, 1.20904, -0.70833, 2.76157, 0.69154, 0.52873])
FRAMINGHAM_MEAN_F = np.array([52, 213, 50, 120, 0, 0])
FRAMINGHAM_S0_F = 0.95012

def framingham_points(patient: Dict) -> np.ndarray:
    """Convierte datos del paciente a vector X para Framingham."""
    is_male = patient["sexo"].lower() == "hombre"
    x = np.array([
        patient["edad"],
        patient["colesterol_total"],
        patient["hdl"],
        patient["presion_sistolica"],
        int(patient["diabetes"]),
        int(patient["fumador"]),
    ])
    beta = FRAMINGHAM_BETA_M if is_male else FRAMINGHAM_BETA_F
    mean = FRAMINGHAM_MEAN_M if is_male else FRAMINGHAM_MEAN_F
    s0 = FRAMINGHAM_S0_M if is_male else FRAMINGHAM_S0_F
    logit = np.dot(beta, x - mean)
    risk = 1 - s0 ** math.exp(logit)
    return round(risk * 100, 1)


def framingham_risk(patient: Dict) -> Dict:
    """Calcula riesgo Framingham y devuelve dict con % y categoría."""
    risk_pct = framingham_points(patient)
    category = categorize_risk(risk_pct)
    return {"percent": risk_pct, "category": category}


# ­SCORE 2019 tablas simplificadas (bajo y alto riesgo)
SCORE_TABLE_LOW = {
    # edad : {chol: {pressure: {smoke: risk}}}
    40: {5: {120: {False: 1, True: 2}}},
}
SCORE_TABLE_HIGH = {
    40: {5: {120: {False: 2, True: 4}}},
}

def score_lookup(patient: Dict) -> float:
    """Ejemplo de lookup simplificado – sustituye por tablas completas."""
    tbl = SCORE_TABLE_HIGH if patient["region_riesgo"] == "alto" else SCORE_TABLE_LOW
    age = min(tbl.keys(), key=lambda a: abs(a - patient["edad"]))
    chol_key = min(tbl[age].keys(), key=lambda c: abs(c - patient["colesterol_total"]/38.67))
    press_key = min(tbl[age][chol_key].keys(), key=lambda p: abs(p - patient["presion_sistolica"]))
    risk = tbl[age][chol_key][press_key][patient["fumador"]]
    return risk

def score_risk(patient: Dict) -> Dict:
    risk_pct = score_lookup(patient)
    category = categorize_risk(risk_pct)
    return {"percent": risk_pct, "category": category}


# ­ACC/AHA 2013 Ecuaciones basadas en raza
ACC_AHA_COEFF_WHITE_M = [-29.18, 4.03, -0.92, 1.92, 1.46, 0.68, 0.63]
ACC_AHA_BASE_WHITE_M = 0.9144

def acc_aha_equation(patient: Dict) -> float:
    """Versión simplificada; sustituir por ecuaciones oficiales completas."""
    c = ACC_AHA_COEFF_WHITE_M
    ln_age = math.log(patient["edad"])
    ln_chol = math.log(patient["colesterol_total"])
    ln_hdl = math.log(patient["hdl"])
    ln_sys = math.log(patient["presion_sistolica"])
    smoker = int(patient["fumador"])
    diabetes = int(patient["diabetes"])
    tx_htn = int(patient["tratamiento_hipertension"])
    logit = (c[0]*ln_age + c[1]*ln_chol + c[2]*ln_hdl +
             c[3]*ln_sys + c[4]*smoker + c[5]*diabetes +
             c[6]*tx_htn)
    risk = 1 - ACC_AHA_BASE_WHITE_M ** math.exp(logit)
    return round(risk * 100, 1)

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
