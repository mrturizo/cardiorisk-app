# Reglas de implementación, validación y categorización

## 1) Entradas y unidades (comunes)
- edad: años (int/float)
- sexo: "hombre" | "mujer"
- presion_sistolica: mmHg
- colesterol_total: mg/dL
- hdl: mg/dL
- no_hdl (opcional): mg/dL (si no se provee, calcular como TC − HDL)
- tratamiento_hipertension: bool
- fumador: bool
- diabetes: bool (solo requerido en PCE)
- region_riesgo (SCORE2): "bajo" | "moderado" | "alto" | "muy_alto"

## 2) Framingham (D'Agostino 2008)
- Implementación: `backend/calculators.py` (coeficientes verificados por sexo).
- Transformaciones: ln(edad), ln(TC), ln(HDL), ln(PAS); coef distinto si PAS tratada.
- Fórmula: riesgo = 1 − S0^exp(L − meanL)
- Categorías (10a CVD):
  - <10%: bajo
  - 10–20%: intermedio
  - >20%: alto
- Validación mínima: 3 casos de referencia por sexo comparando con tablas/framingham calculators.

## 3) SCORE2 (ESC 2021)
- Ruta preferente: tablas oficiales (si `backend/score2_risk_tables.json` está completo) usando `backend/score2_tables.py`.
- Fallback continuo: `score2_lookup()` con estructura Cox/Fine‑Gray (ln edad, ln edad^2, ln PAS, ln no‑HDL, fumador) y calibración regional.
- Entradas válidas: edad 40–89; PAS 100–179; no‑HDL 3.0–7.9 mmol/L (o TC−HDL convertido por 38.67).
- Categorías por edad (ESC):
  - 40–49: <2.5% bajo‑mod; 2.5–<7.5% alto; ≥7.5% muy alto
  - 50–69: <5% bajo‑mod; 5–<10% alto; ≥10% muy alto
  - 70–89: <7.5% bajo‑mod; 7.5–<15% alto; ≥15% muy alto
- Validación: 5 puntos por región/sexo contra la tabla (o MDCalc) y comprobar coincidencia exacta cuando se use la ruta de tablas.

## 4) ACC/AHA (PCE 2013)
- Implementación directa en `acc_aha_equation()` para población blanca (hombre/mujer) con todas las interacciones publicadas (ln_age×ln_tc, ln_age×ln_hdl, ln_age×ln_sbp_tr/ut, ln_age×smoker; y ln_age^2 en mujeres).
- Clamps: edad 40–79; TC 130–320; HDL 20–90; PAS 90–200.
- Fórmula: riesgo = 1 − S0^exp(L − meanXB)
- Categorías (ASCVD 10a):
  - <5%: bajo
  - 5–7.5%: limítrofe
  - 7.5–20%: intermedio
  - ≥20%: alto
- Validación: 3 casos por sexo blanco con calculadora ACC/AHA.

## 5) Validación automatizada (sugerida)
- Crear `tests/validation_cases.json` con casos esperados y un script `scripts/validate.py` que ejecute cada escala y compare tolerancia (0% para ruta de tablas; ≤0.2 pp para ecuaciones).

## 6) Reglas de errores y clamps
- Si falta una entrada obligatoria, retornar error estructurado.
- Aplicar clamps antes de logaritmos.
- Limitar salida: Framingham 0–100%, SCORE2 0–50%, PCE 0–40%.

## 7) Documentación al usuario
- Indicar siempre las unidades requeridas y si se está usando no‑HDL derivado (TC−HDL).
- Mostrar método usado para SCORE2 (tablas, coeficientes o fallback continuo).
