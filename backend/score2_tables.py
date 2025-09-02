from typing import Dict, Optional, Tuple
import json
import os

# Estructura esperada del JSON (score2_risk_tables.json):
# {
#   "metadata": { "source": "ESC SCORE2 charts", "region": ["low","moderate","high","very_high"] },
#   "SCORE2": {
#     "low": {
#       "women": {
#         "ages": [[40,44],[45,49],...,[65,69]],
#         "sbp_bands": [[100,119],[120,139],[140,159],[160,179]],
#         "non_hdl_bands": [3.0,3.9,4.9,5.9,6.9,7.9],  # límites superiores mmol/L
#         "values": { "non_smoker": [[[...]]], "smoker": [[[...]]] }
#       },
#       "men": { ... }
#     },
#     "moderate": { ... },
#     ...
#   },
#   "SCORE2_OP": {
#      "low": { ... }  # 70–89
#   }
# }

_JSON_NAME = "score2_risk_tables.json"


def _load_tables_json() -> Optional[Dict]:
    here = os.path.dirname(__file__)
    path = os.path.join(here, _JSON_NAME)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        # Validación mínima
        if not data.get("SCORE2"):
            return None
        return data
    except Exception:
        return None


def _find_band_index(value: float, bands: list) -> int:
    """Devuelve el índice de banda para un valor dado.
    - Para bandas de edad y PAS: se definen como [low, high].
    - Para no-HDL mmol/L: lista de límites superiores (estilo histograma).
    """
    if not bands:
        return -1
    # Caso bandas como pares [low, high]
    if isinstance(bands[0], list) and len(bands[0]) == 2:
        for idx, (low, high) in enumerate(bands):
            if value >= low and value <= high:
                return idx
        return -1
    # Caso límites superiores
    for idx, upper in enumerate(bands):
        if value <= upper:
            return idx
    return len(bands) - 1


def score2_lookup_from_tables(patient: Dict) -> Optional[Tuple[float, str, Dict]]:
    """Devuelve (percent, category, meta) desde tablas oficiales si existen.
    Retorna None si no hay tablas o si no se encuentra coincidencia.
    """
    data = _load_tables_json()
    if not data:
        return None

    region_input = str(patient.get("region_riesgo", "moderate")).lower().replace(" ", "_").replace("-", "_")
    region_map = {"bajo": "low", "low": "low", "moderado": "moderate", "moderate": "moderate", "alto": "high", "high": "high", "muy_alto": "very_high", "muy-alto": "very_high", "very_high": "very_high"}
    region = region_map.get(region_input, "moderate")

    sexo = str(patient.get("sexo", "hombre")).lower()
    sex_key = "men" if sexo == "hombre" else "women"

    edad = float(patient["edad"])
    sbp = float(patient["presion_sistolica"])

    # Preferir no-HDL si viene, si no calcular como TC - HDL; convertir a mmol/L
    if "no_hdl" in patient:
        no_hdl_mmol = float(patient["no_hdl"]) / 38.67
    else:
        tc = float(patient.get("colesterol_total", 200.0))
        hdl = float(patient.get("hdl", 50.0))
        no_hdl_mmol = max(0.0, (tc - hdl)) / 38.67

    smoker = bool(patient.get("fumador", False))

    # Seleccionar tabla: SCORE2 40–69 o SCORE2-OP 70–89
    table_group = "SCORE2_OP" if edad >= 70 else "SCORE2"
    group = data.get(table_group, {}).get(region, {}).get(sex_key)
    if not group:
        return None

    age_idx = _find_band_index(edad, group.get("ages", []))
    sbp_idx = _find_band_index(sbp, group.get("sbp_bands", []))
    chol_idx = _find_band_index(no_hdl_mmol, group.get("non_hdl_bands", []))
    if min(age_idx, sbp_idx, chol_idx) < 0:
        return None

    grid_key = "smoker" if smoker else "non_smoker"
    try:
        value = group["values"][grid_key][age_idx][sbp_idx][chol_idx]
    except Exception:
        return None

    if value is None:
        return None

    # Categoría por colores oficial (<2.5, 2.5–<7.5, 7.5–<15, ≥15)
    pct = float(value)
    if pct < 2.5:
        category = "bajo"
    elif pct < 7.5:
        category = "moderado"
    elif pct < 15:
        category = "alto"
    else:
        category = "muy_alto"

    meta = {
        "used_table": table_group,
        "region": region,
        "sex": sex_key,
        "age_band_index": age_idx,
        "sbp_band_index": sbp_idx,
        "non_hdl_band_index": chol_idx
    }
    return pct, category, meta
