"""
Validación de datos clínicos y advertencias médicas
"""

from typing import Tuple, List, Dict

RANGES = {
    "edad": (20, 79),
    "presion_sistolica": (90, 200),
    "colesterol_total": (100, 400),
    "hdl": (20, 100),
}


def validate_patient_data(data: Dict) -> Tuple[bool, List[str]]:
    """
    Devuelve (True, warnings) si es válido o (False, errors) si hay errores.
    """
    errors, warnings = [], []

    for key, (low, high) in RANGES.items():
        if key not in data:
            errors.append(f"Falta el parámetro {key}")
            continue
        value = data[key]
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            errors.append(f"{key} no es numérico")
            continue
        if not (low <= numeric <= high):
            errors.append(f"{key} fuera de rango ({low}-{high})")
        elif numeric in (low, high):
            warnings.append(f"{key} en el límite permitido")

    # Campo sexo
    sexo = data.get("sexo")
    if sexo is None:
        errors.append("Falta el parámetro sexo")
    else:
        s = str(sexo).lower()
        if s not in ("hombre", "mujer"):
            errors.append("sexo debe ser 'hombre' o 'mujer'")

    # Campos booleanos obligatorios
    bool_fields = ["fumador", "diabetes", "tratamiento_hipertension"]
    for bf in bool_fields:
        if bf not in data:
            errors.append(f"Falta el parámetro {bf}")
        elif not isinstance(data[bf], bool):
            warnings.append(f"{bf} debería ser booleano")

    return (len(errors) == 0, errors if errors else warnings)
