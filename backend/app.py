"""
Servidor Flask principal para la Calculadora de Riesgo Cardiovascular
Autor: <tu-nombre>
Licencia: MIT
"""

from datetime import datetime, timedelta
from uuid import uuid4

from flask import Flask, request, jsonify, send_file
from werkzeug.exceptions import HTTPException
from flask_cors import CORS

from calculators import (
    framingham_risk,
    score_risk,
    acc_aha_risk,
)
from validators import validate_patient_data
from report_generator import build_pdf_report

# ­In-memory store con expiración de 1 hora
SESSIONS = {}
EXPIRE_MINUTES = 60

app = Flask(__name__)
# Habilitar CORS para todos los endpoints del backend
CORS(app)


@app.after_request
def add_cors_headers(response):
    """Asegura encabezados CORS para peticiones desde archivo o puertos distintos."""
    response.headers.setdefault("Access-Control-Allow-Origin", "*")
    response.headers.setdefault("Access-Control-Allow-Headers", "Content-Type")
    response.headers.setdefault("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    return response


def _cleanup_expired():
    """Elimina resultados almacenados con más de EXPIRE_MINUTES."""
    now = datetime.utcnow()
    expired = [
        sid for sid, data in SESSIONS.items()
        if now - data["timestamp"] > timedelta(minutes=EXPIRE_MINUTES)
    ]
    for sid in expired:
        del SESSIONS[sid]


@app.route("/calculate/<string:method>", methods=["POST"])
def calculate(method):
    """
    Calcula riesgo según el método indicado:
    framingham | score | acc-aha | all
    """
    _cleanup_expired()
    patient = request.json or {}

    # Validación de datos de entrada
    ok, warnings_or_errors = validate_patient_data(patient)
    if not ok:
        return jsonify({"status": "error", "errors": warnings_or_errors}), 400

    result = {}
    try:
        if method in ("framingham", "all"):
            result["framingham"] = framingham_risk(patient)
        if method in ("score", "all"):
            result["score"] = score_risk(patient)
        if method in ("acc-aha", "all"):
            result["acc_aha"] = acc_aha_risk(patient)
    except ValueError as err:
        # Algoritmo devolvió error médico
        return jsonify({"status": "error", "errors": [str(err)]}), 422
    except Exception as err:  # Fallback a JSON legible en caso de error inesperado
        return jsonify({"status": "error", "errors": [f"Error interno: {type(err).__name__}: {err}"]}), 500

    # Almacenar sesión temporal
    session_id = str(uuid4())
    SESSIONS[session_id] = {
        "timestamp": datetime.utcnow(),
        "patient": patient,
        "result": result,
        "warnings": warnings_or_errors,
    }
    return jsonify({
        "status": "ok",
        "session_id": session_id,
        "result": result,
        "warnings": warnings_or_errors,
    })


# Respuestas a preflight explícitas (por si el navegador exige OPTIONS)
@app.route("/calculate/<string:method>", methods=["OPTIONS"])
def calculate_options(method):
    return ("", 204)


@app.route("/generate-report/<string:session_id>", methods=["GET"])
def generate_report(session_id):
    """Genera un PDF profesional con los resultados almacenados."""
    _cleanup_expired()
    data = SESSIONS.get(session_id)
    if not data:
        return jsonify({"status": "error", "errors": ["Sesión no encontrada"]}), 404

    pdf_path = build_pdf_report(
        patient=data["patient"],
        result=data["result"],
        warnings=data["warnings"],
    )
    return send_file(pdf_path, as_attachment=True)


@app.route("/generate-report/<string:session_id>", methods=["OPTIONS"])
def report_options(session_id):
    return ("", 204)


# Manejo global de errores para devolver JSON coherente (incluye HTTPException)
@app.errorhandler(HTTPException)
def handle_http_exception(err: HTTPException):
    response = err.get_response()
    response.data = jsonify({
        "status": "error",
        "errors": [err.description or err.name],
    }).get_data()
    response.content_type = "application/json"
    return response


@app.errorhandler(Exception)
def handle_unexpected_exception(err: Exception):
    # Log en consola y JSON con mensaje genérico
    try:
        app.logger.exception("Unhandled exception: %s", err)
    except Exception:
        pass
    return jsonify({
        "status": "error",
        "errors": [f"Error interno: {type(err).__name__}: {err}"],
    }), 500


@app.route("/", methods=["GET"])  # Ruta simple para salud
def health():
    return jsonify({"status": "ok", "message": "API OK"})


@app.route("/health", methods=["GET"])  # Alias de salud
def health_alt():
    return jsonify({"status": "ok", "message": "API OK"})


@app.route("/healthz", methods=["GET"])  # Otro alias común
def healthz():
    return jsonify({"status": "ok", "message": "API OK"})


if __name__ == "__main__":
    # Mostrar rutas registradas para verificación
    try:
        print("Rutas registradas:")
        print(app.url_map)
    except Exception:
        pass
    app.run(host="0.0.0.0", port=5000, debug=True)
