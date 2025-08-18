/* Lógica principal en JavaScript ES6+ */
const API_URL = "http://localhost:5000";
const form = document.getElementById("risk-form");
const resultsSection = document.getElementById("results");
const chartsDiv = document.getElementById("charts");
const interpretationDiv = document.getElementById("interpretation");
const btnPdf = document.getElementById("btn-pdf");
let currentSessionId = null;

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!validateForm()) return;

  btnPdf.disabled = true;
  interpretationDiv.textContent = "";
  chartsDiv.innerHTML = "";
  resultsSection.classList.add("hidden");

  const data = Object.fromEntries(new FormData(form).entries());

  // Convertir checkboxes a booleanos
  ["fumador","diabetes","tratamiento_hipertension","estatinas"].forEach(
    k => data[k] = form.elements[k].checked
  );
  data.region_riesgo = "alto"; // simplificación para SCORE

  try {
    const res = await fetch(`${API_URL}/calculate/all`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify(data)
    });
    const json = await res.json();
    if (json.status !== "ok") throw new Error(json.errors.join(", "));

    currentSessionId = json.session_id;
    displayResults(json.result);
    btnPdf.disabled = false;
  } catch(err){
    alert("Error: " + err.message);
  }
});

btnPdf.addEventListener("click", async () => {
  if (!currentSessionId) return;
  const url = `${API_URL}/generate-report/${currentSessionId}`;
  window.open(url,"_blank");
});

function validateForm(){
  // Ejemplo mínimo: edad y colesterol total
  const edad = +form.elements["edad"].value;
  const col = +form.elements["colesterol_total"].value;
  if (edad < 20 || edad > 79){
    alert("Edad fuera de rango (20-79)");
    return false;
  }
  if (col < 100 || col > 400){
    alert("Colesterol total fuera de rango (100-400)");
    return false;
  }
  return true;
}

function displayResults(result){
  resultsSection.classList.remove("hidden");

  // Interpretación textual
  const overall = Math.max(
    result.framingham.percent,
    result.score.percent,
    result.acc_aha.percent
  );
  let riskCategory = "bajo";
  if (overall >=20) riskCategory="muy alto";
  else if (overall >=10) riskCategory="alto";
  else if (overall >=5) riskCategory="moderado";

  interpretationDiv.innerHTML =
    `<p>Riesgo global: <strong>${overall}%</strong> (${riskCategory})</p>`;

  generateCharts(result);
}
