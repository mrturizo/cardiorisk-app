# Casos de referencia – CardioRisk (validados)

A continuación se documentan tres casos representativos con sus salidas actuales por escala. Estos valores sirven como referencia para pruebas de regresión.

## Caso 1 – Varón 55 fumador
Entradas: edad 55, sexo hombre, TC 200 mg/dL, HDL 45 mg/dL, PAS 140 mmHg, HTA tratada: no, fumador: sí, diabetes: no, región SCORE2: moderado.

- Framingham: 25.0% (alto)
- SCORE2: 4.3% (bajo)
- ACC/AHA: 13.2% (intermedio)

## Caso 2 – Mujer 65 HTA tratada DM
Entradas: edad 65, sexo mujer, TC 250 mg/dL, HDL 35 mg/dL, PAS 160 mmHg, HTA tratada: sí, fumador: no, diabetes: sí, región SCORE2: alto.

- Framingham: 53.4% (alto)
- SCORE2: 1.3% (bajo)
- ACC/AHA: 27.6% (alto)

## Caso 3 – Varón 45 sano
Entradas: edad 45, sexo hombre, TC 180 mg/dL, HDL 55 mg/dL, PAS 120 mmHg, HTA tratada: no, fumador: no, diabetes: no, región SCORE2: bajo.

- Framingham: 4.3% (bajo)
- SCORE2: 1.1% (bajo)
- ACC/AHA: 1.3% (bajo)

Notas:
- Los rangos de categorización por escala se describen en `rules/IMPLEMENTACION_Y_VALIDACION.md`.
- SCORE2 usa el modelo continuo con clamps; si se cargan tablas oficiales, los porcentajes pueden variar para coincidir con la tabla exacta.
