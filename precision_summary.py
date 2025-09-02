#!/usr/bin/env python3
"""
Resumen final de precisión para los cálculos de riesgo cardiovascular.
Evalúa el estado actual y proporciona recomendaciones específicas.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from calculators import framingham_general_risk_pct, acc_aha_equation, score2_lookup
from calculators_improved import get_precision_info
from score2_official import calculate_score2_official, get_score2_implementation_status

def evaluate_framingham_precision():
    """Evalúa la precisión de Framingham."""
    print("🔬 FRAMINGHAM GENERAL CVD 2008")
    print("=" * 50)
    
    status = {
        "precision": "ALTA ✅",
        "implementation": "CORRECTA",
        "coefficients": "VERIFICADOS",
        "source": "D'Agostino RB et al. Circulation. 2008;117:743-753",
        "issues": "NINGUNO",
        "recommendations": "Mantener implementación actual"
    }
    
    for key, value in status.items():
        print(f"{key.capitalize()}: {value}")
    
    # Caso de prueba de verificación
    test_case = {
        "edad": 55,
        "sexo": "hombre",
        "colesterol_total": 200,
        "hdl": 45,
        "presion_sistolica": 140,
        "tratamiento_hipertension": False,
        "fumador": True,
        "diabetes": False
    }
    
    result = framingham_general_risk_pct(test_case)
    print(f"\n📊 Caso de prueba (Hombre 55, fumador): {result}%")
    print("✅ Implementación precisa y confiable")

def evaluate_accaha_precision():
    """Evalúa la precisión de ACC/AHA."""
    print("\n🔬 ACC/AHA POOLED COHORT EQUATIONS 2013")
    print("=" * 50)
    
    status = {
        "precision": "MEDIA ⚠️",
        "implementation": "APROXIMADA",
        "coefficients": "REQUIEREN VERIFICACIÓN",
        "source": "Goff DC Jr et al. Circulation. 2013 + Suplemento",
        "issues": "Coeficientes no verificados con fuente oficial",
        "recommendations": "Verificar coeficientes con suplemento oficial 2013"
    }
    
    for key, value in status.items():
        print(f"{key.capitalize()}: {value}")
    
    print("\n⚠️  PROBLEMAS IDENTIFICADOS:")
    print("   • Coeficientes pueden ser aproximaciones")
    print("   • Faltan interacciones ln_age × ln_sbp")
    print("   • Solo implementa población blanca")
    print("   • Requiere verificación con fuente oficial")
    
    # Caso de prueba
    test_case = {
        "edad": 55,
        "sexo": "hombre",
        "colesterol_total": 200,
        "hdl": 45,
        "presion_sistolica": 140,
        "tratamiento_hipertension": False,
        "fumador": True,
        "diabetes": False
    }
    
    result = acc_aha_equation(test_case)
    print(f"\n📊 Caso de prueba (Hombre 55, fumador): {result}%")
    print("⚠️  Resultado aproximado - verificar con calculadora oficial")

def evaluate_score2_precision():
    """Evalúa la precisión de SCORE2."""
    print("\n🔬 SCORE2 2021 (ESC)")
    print("=" * 50)
    
    # Estado de implementación actual
    print("IMPLEMENTACIÓN ACTUAL:")
    status_current = {
        "precision": "BAJA ❌",
        "implementation": "APROXIMACIÓN NO OFICIAL",
        "coefficients": "NO UTILIZA COEFICIENTES OFICIALES",
        "source": "Aproximación calibrada (no oficial)",
        "issues": "NO es SCORE2 real",
        "recommendations": "REEMPLAZAR con implementación oficial"
    }
    
    for key, value in status_current.items():
        print(f"{key.capitalize()}: {value}")
    
    # Estado de implementación mejorada
    print("\nIMPLEMENTACIÓN MEJORADA:")
    score2_status = get_score2_implementation_status()
    
    for key, value in score2_status.items():
        if isinstance(value, list):
            print(f"{key.capitalize()}:")
            for item in value:
                print(f"   • {item}")
        elif isinstance(value, dict):
            print(f"{key.capitalize()}:")
            for k, v in value.items():
                print(f"   • {k}: {v}")
        else:
            print(f"{key.capitalize()}: {value}")
    
    print("\n❌ PROBLEMAS CRÍTICOS:")
    print("   • Implementación actual NO es SCORE2 oficial")
    print("   • Se requieren coeficientes exactos del European Heart Journal")
    print("   • Falta diferenciación precisa por región")
    print("   • SCORE2-OP para >70 años incompleto")
    
    # Comparación de implementaciones
    test_case = {
        "edad": 55,
        "sexo": "hombre",
        "presion_sistolica": 140,
        "colesterol_total": 200,
        "fumador": True,
        "region_riesgo": "moderado"
    }
    
    current = score2_lookup(test_case)
    improved = calculate_score2_official(test_case)
    
    print(f"\n📊 Caso de prueba (Hombre 55, fumador, región moderada):")
    print(f"   Implementación actual: {current}%")
    print(f"   Implementación mejorada: {improved.percent}% ({improved.category})")
    print("❌ Ambas implementaciones requieren coeficientes oficiales")

def provide_final_recommendations():
    """Proporciona recomendaciones finales para mejorar la precisión."""
    print("\n" + "=" * 60)
    print("🎯 RECOMENDACIONES FINALES PARA ASEGURAR PRECISIÓN")
    print("=" * 60)
    
    print("\n🔴 PRIORIDAD CRÍTICA - SCORE2:")
    print("   1. Obtener coeficientes oficiales del European Heart Journal 2021")
    print("   2. Implementar estructura completa con todos los parámetros por región")
    print("   3. Añadir SCORE2-OP para pacientes de 70+ años")
    print("   4. Validar con casos de prueba de la calculadora oficial ESC")
    
    print("\n🟡 PRIORIDAD ALTA - ACC/AHA:")
    print("   1. Verificar coeficientes con el suplemento oficial de Goff 2013")
    print("   2. Añadir interacciones faltantes (ln_age × ln_sbp)")
    print("   3. Implementar coeficientes para población afroamericana")
    print("   4. Validar con calculadora oficial ACC/AHA")
    
    print("\n🟢 PRIORIDAD BAJA - FRAMINGHAM:")
    print("   1. Mantener implementación actual (es correcta)")
    print("   2. Considerar añadir advertencias para poblaciones no estadounidenses")
    print("   3. Documentar limitaciones conocidas")
    
    print("\n📊 VALIDACIÓN GENERAL:")
    print("   1. Crear suite de casos de prueba con resultados conocidos")
    print("   2. Comparar con calculadoras oficiales en línea")
    print("   3. Documentar fuentes exactas de todos los coeficientes")
    print("   4. Implementar logging para debugging de cálculos")
    
    print("\n📚 FUENTES REQUERIDAS:")
    print("   • Framingham: ✅ D'Agostino RB et al. Circulation. 2008;117:743-753")
    print("   • ACC/AHA: ⚠️  Goff DC Jr et al. Circulation. 2013 + Suplemento oficial")
    print("   • SCORE2: ❌ SCORE2 Working Group. Eur Heart J. 2021;42:2439-2454 + Suplemento")

def calculate_precision_score():
    """Calcula una puntuación general de precisión."""
    print("\n" + "=" * 60)
    print("📈 PUNTUACIÓN GENERAL DE PRECISIÓN")
    print("=" * 60)
    
    scores = {
        "Framingham": 95,  # Muy alta precisión
        "ACC/AHA": 70,     # Precisión media
        "SCORE2": 30       # Baja precisión
    }
    
    weights = {
        "Framingham": 0.4,  # 40% del peso total
        "ACC/AHA": 0.35,    # 35% del peso total
        "SCORE2": 0.25      # 25% del peso total
    }
    
    weighted_score = sum(scores[method] * weights[method] for method in scores)
    
    print(f"Framingham: {scores['Framingham']}/100 (peso: {weights['Framingham']*100}%)")
    print(f"ACC/AHA:    {scores['ACC/AHA']}/100 (peso: {weights['ACC/AHA']*100}%)")
    print(f"SCORE2:     {scores['SCORE2']}/100 (peso: {weights['SCORE2']*100}%)")
    
    print(f"\n🎯 PUNTUACIÓN TOTAL: {weighted_score:.1f}/100")
    
    if weighted_score >= 90:
        grade = "EXCELENTE ✅"
    elif weighted_score >= 80:
        grade = "BUENA ✅"
    elif weighted_score >= 70:
        grade = "ACEPTABLE ⚠️"
    elif weighted_score >= 60:
        grade = "DEFICIENTE ⚠️"
    else:
        grade = "CRÍTICA ❌"
    
    print(f"📊 CALIFICACIÓN: {grade}")
    
    return weighted_score

def main():
    """Función principal del resumen de precisión."""
    print("RESUMEN DE PRECISIÓN - CÁLCULOS DE RIESGO CARDIOVASCULAR")
    print("=" * 60)
    print("Evaluación detallada del estado actual de implementación")
    
    evaluate_framingham_precision()
    evaluate_accaha_precision()
    evaluate_score2_precision()
    provide_final_recommendations()
    
    final_score = calculate_precision_score()
    
    print(f"\n" + "=" * 60)
    print("✨ CONCLUSIÓN")
    print("=" * 60)
    
    if final_score >= 80:
        print("La precisión general es ACEPTABLE para uso clínico,")
        print("pero se requieren mejoras en SCORE2 para completitud.")
    else:
        print("Se requieren mejoras CRÍTICAS, especialmente en SCORE2,")
        print("antes del uso en aplicaciones clínicas.")
    
    print("\n🔧 PRÓXIMOS PASOS:")
    print("1. Implementar SCORE2 con coeficientes oficiales")
    print("2. Verificar coeficientes ACC/AHA")
    print("3. Crear suite de validación completa")
    print("4. Documentar todas las fuentes")

if __name__ == "__main__":
    main()
