# Calculadora de Riesgo Cardiovascular

Aplicación web educativa que calcula los principales **scores de riesgo cardiovascular** (Framingham, SCORE y ACC/AHA) a 10 años.

**Atención:**
**Esta versión está intencionalmente hecha con fallos. No se pretende que sea funcional, pero sirve de punto de partida para construir una aplicación funcional en unos pocos pasos** 

## Requisitos

| Software | Versión mínima |
|----------|----------------|
| Python   | 3.8 |
| Node.js  | 18 (solo para servir archivos estáticos opcional) |
| Navegador| Chrome 90 / Firefox 88 / Edge 90 |

## Instalación en Windows 10/11 con VS Code

1. **Clona o descarga** este repositorio  
git clone <URL> calculadora-riesgo
cd calculadora-riesgo

text

2. **Backend**  
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py

El servidor Flask escuchará en `http://localhost:5000`.

3. **Frontend**  
Abre `frontend/index.html` directamente en el navegador o instala la extensión
**Live Server** de VS Code y pulsa _Go Live_ para servirlo.

4. **Uso**  
1. Completa el formulario con los datos del paciente  
2. Pulsa **Calcular Riesgo** para ver los resultados con gráficos  
3. Pulsa **Generar Reporte** para descargar un PDF profesional  

5. **Limpieza automática**  
Los datos en memoria se eliminan después de 60 minutos.

## Seguridad y Privacidad

- Los datos no se guardan en bases de datos ni se transmiten a terceros.  
- Todo cálculo se realiza en memoria y se descarta tras 1 h.

## Licencia

MIT © 2025


> **Disclaimer**  
> Esta calculadora es una herramienta de apoyo educativo. Los resultados **no** sustituyen el criterio médico profesional. Consulte siempre con un profesional de la salud para decisiones médicas.