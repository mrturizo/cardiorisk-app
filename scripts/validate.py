#!/usr/bin/env python3
"""
Validación rápida de las tres escalas.

Ejecuta casos representativos y muestra:
- porcentaje
- categoría
- (para SCORE2) método usado: tablas/oficial/fallback
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(ROOT)

from backend.calculators import framingham_risk, score2_risk, acc_aha_risk


def main() -> None:
    cases = [
        {
            "name": "Caso 1 – Hombre 55a fumador",
            "patient": {
                "edad": 55, "sexo": "hombre",
                "colesterol_total": 200, "hdl": 45,
                "presion_sistolica": 140, "tratamiento_hipertension": False,
                "fumador": True, "diabetes": False, "region_riesgo": "moderado"
            },
        },
        {
            "name": "Caso 2 – Mujer 65a HTA tratada, no fumadora",
            "patient": {
                "edad": 65, "sexo": "mujer",
                "colesterol_total": 250, "hdl": 35,
                "presion_sistolica": 160, "tratamiento_hipertension": True,
                "fumador": False, "diabetes": True, "region_riesgo": "alto"
            },
        },
        {
            "name": "Caso 3 – Hombre 45a sano",
            "patient": {
                "edad": 45, "sexo": "hombre",
                "colesterol_total": 180, "hdl": 55,
                "presion_sistolica": 120, "tratamiento_hipertension": False,
                "fumador": False, "diabetes": False, "region_riesgo": "bajo"
            },
        },
    ]

    for c in cases:
        p = c["patient"]
        print("\n==>", c["name"]) 
        fr = framingham_risk(p)
        sc = score2_risk(p)
        ac = acc_aha_risk(p)
        print("Framingham:", fr)
        print("SCORE2:", sc)
        print("ACC/AHA:", ac)


if __name__ == "__main__":
    main()


