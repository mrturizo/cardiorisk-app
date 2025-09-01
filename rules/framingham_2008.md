# Framingham General CVD (D'Agostino 2008)

- Objetivo: Riesgo a 10 años de enfermedad cardiovascular general.
- Referencia: D'Agostino RB et al. Circulation. 2008.

## Variables de entrada
- edad (años)
- sexo ("hombre" | "mujer")
- colesterol_total (mg/dL)
- hdl (mg/dL)
- presion_sistolica (mmHg)
- tratamiento_hipertension (bool)
- fumador (bool)
- diabetes (bool)

## Ecuación (Cox proporcional)
- Para cada sexo se usan coeficientes distintos β y constantes S0 (supervivencia a 10 años) y meanL.
- Definiciones:
  - ln_age = ln(edad)
  - ln_tc = ln(colesterol_total)
  - ln_hdl = ln(hdl)
  - ln_sbp = ln(presion_sistolica)
- Índice lineal:
  - Hombres: L = 3.06117·ln_age + 1.12370·ln_tc − 0.93263·ln_hdl + (1.99881 si tratado, 1.93303 si no)·ln_sbp + 0.65451·fumador + 0.57367·diabetes
  - Mujeres: L = 2.32888·ln_age + 1.20904·ln_tc − 0.70833·ln_hdl + (2.82263 si tratado, 2.76157 si no)·ln_sbp + 0.69154·fumador + 0.77763·diabetes
- Riesgo a 10 años: riesgo = 1 − S0^(exp(L − meanL))
- S0 y meanL:
  - Hombres: S0 = 0.88936, meanL = 23.9802
  - Mujeres: S0 = 0.95012, meanL = 26.1931

## Pseudocódigo
```
input: edad, sexo, colesterol_total, hdl, presion_sistolica, tratamiento_hipertension, fumador, diabetes
clamp edad to [20,79]; clamp presion_sistolica to [90,200]; clamp hdl to [20,100]; clamp colesterol_total to [100,400]
if sexo == hombre: usar coef_male, S0=0.88936, meanL=23.9802
else: usar coef_female, S0=0.95012, meanL=26.1931
ln_age = ln(edad); ln_tc = ln(colesterol_total); ln_hdl = ln(hdl); ln_sbp = ln(presion_sistolica)
sbp_term = (coef ln_sbp_treated if tratamiento_hipertension else coef ln_sbp_untreated) * ln_sbp
L = coef.ln_age*ln_age + coef.ln_tc*ln_tc + coef.ln_hdl*ln_hdl + sbp_term + coef.smoker*fumador + coef.diabetes*diabetes
riesgo = 1 - (S0 ** exp(L - meanL))
return max(0, min(100, round(100*riesgo, 1)))
```
