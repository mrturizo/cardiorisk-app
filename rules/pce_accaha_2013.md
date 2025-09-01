# Pooled Cohort Equations (ACC/AHA 2013)

- Objetivo: Riesgo a 10 años de ASCVD (IAM no fatal, muerte coronaria, ACV fatal/no fatal) para prevención primaria.
- Referencia: Goff DC Jr. et al., Circulation 2013 (suplemento con coeficientes); tablas por sexo/raza.

## Variables de entrada
- edad (años)
- sexo ("hombre" | "mujer")
- raza ("blanco" | "negro") – si no disponible, usar "blanco"
- colesterol_total (mg/dL)
- hdl (mg/dL)
- presion_sistolica (mmHg)
- tratamiento_hipertension (bool)
- fumador (bool)
- diabetes (bool)

## Ecuación (Cox con interacciones)
- Transformaciones: ln_age = ln(edad), ln_tc = ln(TC), ln_hdl = ln(HDL), ln_sbp = ln(PAS)
- Índice lineal (ejemplo: hombres blancos) incluye términos e interacciones con ln_age:
  - L = β1·ln_age + β2·ln_tc + β3·ln_hdl + β4·ln_sbp_trt + β5·ln_sbp_notrt + β6·fumador + β7·diabetes
  - + interacciones: β8·(ln_age·ln_tc) + β9·(ln_age·ln_hdl) + β10·(ln_age·ln_sbp_trt) + β11·(ln_age·ln_sbp_notrt) + β12·(ln_age·fumador)
- Riesgo a 10 años: riesgo = 1 − S0^(exp(L − meanXB))
- Cada sexo/raza tiene su propio vector β, S0 y meanXB (publicados en el suplemento de 2013).

## Pseudocódigo
```
input: edad, sexo, raza, colesterol_total, hdl, presion_sistolica, tratamiento_hipertension, fumador, diabetes
clamp entradas: edad[40,79]; TC[130,320]; HDL[20,90]; PAS[90,200]
profile = (sexo, raza); coef = COEFS[profile]; S0 = BASE[profile]; meanXB = MEANXB[profile]
ln_age=ln(edad); ln_tc=ln(TC); ln_hdl=ln(HDL); ln_sys=ln(PAS)
ln_sys_trt = ln_sys if tratamiento_hipertension else 0
ln_sys_notrt = ln_sys if not tratamiento_hipertension else 0
L = (b1*ln_age + b2*ln_tc + b3*ln_hdl + b4*ln_sys_trt + b5*ln_sys_notrt + b6*fumador + b7*diabetes
     + b8*ln_age*ln_tc + b9*ln_age*ln_hdl + b10*ln_age*ln_sys_trt + b11*ln_age*ln_sys_notrt + b12*ln_age*fumador)
riesgo = 1 - (S0 ** exp(L - meanXB))
return round(100*riesgo, 1)
```

> Implementación actual en la app usa una versión compacta; para valores oficiales, añadir los vectores β, S0 y meanXB por sexo/raza del suplemento.
