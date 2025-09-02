# CardioRisk – Cálculo de riesgo cardiovascular (Framingham, SCORE2, ACC/AHA)

Este proyecto implementa tres escalas clínicas de riesgo a 10 años:
- Framingham General CVD (D'Agostino 2008)
- SCORE2 (ESC 2021)
- ACC/AHA Pooled Cohort Equations – PCE (2013)

## Estado de precisión
- Framingham: coeficientes oficiales embebidos (alta precisión)
- SCORE2: 
  - Prioriza tablas oficiales si está `backend/score2_risk_tables.json` (lookup exacto)
  - Si no hay tablas, usa un modelo continuo con estructura de Cox (fallback mejorado)
- ACC/AHA (PCE): implementación directa para población blanca con todas las interacciones

## Entradas comunes
- edad (años), sexo ("hombre"|"mujer"), presion_sistolica (mmHg)
- colesterol_total (mg/dL), hdl (mg/dL)
- tratamiento_hipertension (bool), fumador (bool)
- diabetes (bool, solo PCE)
- region_riesgo (SCORE2): "bajo"|"moderado"|"alto"|"muy_alto"
- no_hdl (opcional): mg/dL; si no se provee, se usa TC − HDL (convertido a mmol/L cuando aplica)

## Categorías de riesgo por escala
- Framingham (10a CVD):
  - <10% bajo; 10–20% intermedio; >20% alto
- SCORE2 (ESC 2021):
  - 40–49 años: <2.5% bajo‑mod; 2.5–<7.5% alto; ≥7.5% muy alto
  - 50–69 años: <5% bajo‑mod; 5–<10% alto; ≥10% muy alto
  - 70–89 años: <7.5% bajo‑mod; 7.5–<15% alto; ≥15% muy alto
- ACC/AHA (ASCVD 10a):
  - <5% bajo; 5–7.5% limítrofe; 7.5–20% intermedio; ≥20% alto

## Uso en código
Las funciones de alto nivel están en `backend/calculators.py`:

```python
from backend.calculators import framingham_risk, score2_risk, acc_aha_risk

patient = {
  "edad": 55, "sexo": "hombre",
  "colesterol_total": 200, "hdl": 45,
  "presion_sistolica": 140, "tratamiento_hipertension": False,
  "fumador": True, "diabetes": False, "region_riesgo": "moderado"
}

print(framingham_risk(patient))  # {"percent": ..., "category": "..."}
print(score2_risk(patient))      # prioriza tablas si existen; si no, fallback continuo
print(acc_aha_risk(patient))     # PCE población blanca
```

## Cómo obtener máxima precisión en SCORE2
1. Rellenar `backend/score2_risk_tables.json` con las tablas oficiales (región/sexo/edad/PAS/no‑HDL/fumador) de la ESC 2021.
2. La ruta de tablas se activará automáticamente y devolverá los mismos % de la tabla.

## Reglas y validación
Ver `rules/IMPLEMENTACION_Y_VALIDACION.md` para detalles de entradas, clamps, fórmulas y validación recomendada.

## Notas
- Unidades: mantener mg/dL para lípidos en las entradas. SCORE2 convierte internamente a mmol/L cuando corresponde.
- Límites de salida: Framingham 0–100%, SCORE2 0–50%, ACC/AHA 0–40%.