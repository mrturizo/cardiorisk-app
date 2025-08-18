"""
Servidor Flask principal para la Calculadora de Riesgo Cardiovascular
Autor: <tu-nombre>
Licencia: MIT
"""

from datetime import datetime, timedelta
from uuid import uuid4

from flask import Flask, request, jsonify, send_file
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
CORS(app, resources={r"/calculate/*": {"origins": "*"}})


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
