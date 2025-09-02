# Plan de Mejora de Precisión - Cálculos de Riesgo Cardiovascular

## 🎯 Objetivo
Asegurar la máxima precisión en los cálculos de riesgo cardiovascular para las escalas de Framingham, SCORE y ACC/AHA, cumpliendo con el requisito principal del proyecto.

## 📊 Estado Actual (Puntuación: 70/100 - ACEPTABLE ⚠️)

### ✅ Framingham General CVD 2008 - CORRECTO
- **Precisión**: ALTA (95/100)
- **Estado**: Implementación verificada y correcta
- **Coeficientes**: Verificados con D'Agostino RB et al. Circulation. 2008
- **Acción**: Mantener implementación actual

### ⚠️ ACC/AHA Pooled Cohort Equations 2013 - REQUIERE VERIFICACIÓN
- **Precisión**: MEDIA (70/100)
- **Estado**: Coeficientes aproximados, requieren verificación
- **Problemas**: 
  - Coeficientes no verificados con fuente oficial
  - Faltan interacciones ln_age × ln_sbp
  - Solo población blanca implementada
- **Acción**: Verificar con suplemento oficial Goff 2013

### ❌ SCORE2 2021 - CRÍTICO
- **Precisión**: BAJA (30/100)
- **Estado**: Implementación NO oficial
- **Problemas**:
  - No utiliza coeficientes del European Heart Journal
  - Aproximación calibrada manual
  - Falta diferenciación precisa por región
  - SCORE2-OP incompleto para >70 años
- **Acción**: Implementación completa requerida

## 🔧 Plan de Implementación

### Fase 1: Correcciones Críticas (Inmediato)

#### 1.1 SCORE2 - Implementación Oficial
```
PRIORIDAD: CRÍTICA 🔴
TIEMPO ESTIMADO: 3-5 días
COMPLEJIDAD: ALTA
```

**Tareas específicas:**
- [ ] Obtener coeficientes exactos del European Heart Journal 2021 Supplement
- [ ] Implementar estructura completa por región (bajo, moderado, alto, muy alto riesgo)
- [ ] Añadir coeficientes diferenciados por sexo
- [ ] Implementar SCORE2-OP para pacientes de 70+ años
- [ ] Validar con casos de prueba de la calculadora oficial ESC

**Archivos a modificar:**
- `backend/score2_official.py` - Completar coeficientes
- `backend/calculators.py` - Reemplazar implementación actual
- Crear casos de prueba específicos

#### 1.2 ACC/AHA - Verificación de Coeficientes
```
PRIORIDAD: ALTA 🟡
TIEMPO ESTIMADO: 2-3 días
COMPLEJIDAD: MEDIA
```

**Tareas específicas:**
- [ ] Obtener suplemento oficial de Goff DC Jr et al. Circulation 2013
- [ ] Verificar todos los coeficientes actuales
- [ ] Añadir interacciones faltantes (ln_age × ln_sbp_treated, ln_age × ln_sbp_untreated)
- [ ] Implementar coeficientes para población afroamericana
- [ ] Validar con calculadora oficial ACC/AHA

**Archivos a modificar:**
- `backend/calculators.py` - Corregir coeficientes ACC/AHA
- Añadir coeficientes para todas las poblaciones

### Fase 2: Validación y Testing (Seguimiento)

#### 2.1 Suite de Validación Completa
```
PRIORIDAD: ALTA 🟡
TIEMPO ESTIMADO: 2 días
COMPLEJIDAD: MEDIA
```

**Componentes:**
- [ ] Casos de prueba con resultados conocidos para cada escala
- [ ] Comparación automática con calculadoras oficiales
- [ ] Tests de regresión para cambios futuros
- [ ] Validación de casos extremos y límites

#### 2.2 Documentación y Trazabilidad
```
PRIORIDAD: MEDIA 🟢
TIEMPO ESTIMADO: 1 día
COMPLEJIDAD: BAJA
```

**Entregables:**
- [ ] Documentación completa de fuentes para cada coeficiente
- [ ] Casos de prueba documentados con resultados esperados
- [ ] Guía de validación para futuras actualizaciones
- [ ] Log de cambios y versiones de coeficientes

### Fase 3: Mejoras Adicionales (Opcional)

#### 3.1 Características Avanzadas
- [ ] Advertencias para poblaciones no validadas
- [ ] Logging detallado de cálculos para debugging
- [ ] Interfaz mejorada con información de precisión
- [ ] Exportación de resultados con metadatos

## 📚 Fuentes Oficiales Requeridas

### ✅ Framingham (Ya disponible)
- **Fuente**: D'Agostino RB et al. General cardiovascular risk profile for use in primary care. Circulation. 2008;117:743-753.
- **Estado**: Coeficientes verificados e implementados correctamente

### ⚠️ ACC/AHA (Requiere verificación)
- **Fuente Principal**: Goff DC Jr et al. 2013 ACC/AHA guideline on the assessment of cardiovascular risk. Circulation. 2013;128:2935-2951.
- **Fuente Crítica**: Suplemento oficial con coeficientes exactos
- **Estado**: Coeficientes aproximados, requieren verificación

### ❌ SCORE2 (Crítico - No disponible)
- **Fuente Principal**: SCORE2 Working Group and ESC Cardiovascular Risk Collaboration. SCORE2 risk prediction algorithms: new models to estimate 10-year risk of cardiovascular disease in Europe. Eur Heart J. 2021;42(25):2439-2454.
- **Fuente Crítica**: Suplemento con coeficientes por región y sexo
- **Estado**: No implementado con coeficientes oficiales

## 🎯 Criterios de Éxito

### Objetivos de Precisión
- **Framingham**: Mantener precisión actual (95/100) ✅
- **ACC/AHA**: Alcanzar precisión alta (≥85/100)
- **SCORE2**: Alcanzar precisión alta (≥85/100)
- **Puntuación General**: ≥85/100 (BUENA)

### Validación Técnica
- [ ] Todos los coeficientes verificados con fuentes oficiales
- [ ] Casos de prueba pasan al 100%
- [ ] Comparación exitosa con calculadoras oficiales
- [ ] Sin discrepancias significativas (>1%) en casos estándar

### Documentación
- [ ] Fuentes documentadas para cada coeficiente
- [ ] Casos de prueba documentados
- [ ] Limitaciones conocidas documentadas
- [ ] Guía de mantenimiento creada

## 📈 Impacto Esperado

### Antes (Estado Actual)
- Framingham: Preciso ✅
- ACC/AHA: Aproximado ⚠️
- SCORE2: No confiable ❌
- **Puntuación General**: 70/100

### Después (Meta)
- Framingham: Preciso ✅
- ACC/AHA: Preciso ✅
- SCORE2: Preciso ✅
- **Puntuación General**: ≥85/100

## 🚨 Riesgos y Mitigación

### Riesgo 1: Coeficientes SCORE2 no disponibles públicamente
- **Probabilidad**: Media
- **Impacto**: Alto
- **Mitigación**: Contactar con ESC o buscar implementaciones oficiales abiertas

### Riesgo 2: Discrepancias en interpretación de coeficientes ACC/AHA
- **Probabilidad**: Baja
- **Impacto**: Medio
- **Mitigación**: Validación cruzada con múltiples fuentes y calculadoras

### Riesgo 3: Cambios en implementación actual afecten funcionalidad
- **Probabilidad**: Baja
- **Impacto**: Alto
- **Mitigación**: Tests de regresión completos antes de deployment

## 📋 Checklist de Implementación

### Pre-implementación
- [ ] Backup completo del código actual
- [ ] Identificación de todas las fuentes oficiales
- [ ] Casos de prueba de referencia documentados

### Durante implementación
- [ ] Implementación incremental por escala
- [ ] Validación continua con casos de prueba
- [ ] Documentación de cada cambio

### Post-implementación
- [ ] Validación completa con calculadoras oficiales
- [ ] Tests de regresión exitosos
- [ ] Documentación actualizada
- [ ] Plan de mantenimiento establecido

---

**Responsable**: Equipo de desarrollo
**Fecha límite**: [Definir según cronograma del proyecto]
**Revisión**: Antes de deployment en producción
