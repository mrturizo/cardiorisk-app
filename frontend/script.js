/* Lógica principal en JavaScript ES6+ */
const API_URL = "http://127.0.0.1:5000";
const form = document.getElementById("risk-form");
const resultsSection = document.getElementById("results");
const chartsDiv = document.getElementById("charts");
const interpretationDiv = document.getElementById("interpretation");
const btnPdf = document.getElementById("btn-pdf");
const profileSelect = document.getElementById("profile-select");
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
    if (!res.ok){
      const text = await res.text();
      throw new Error(`HTTP ${res.status} ${res.statusText}${text?` - ${text}`:""}`);
    }
    const json = await res.json();
    if (json.status !== "ok") throw new Error((json.errors||[]).join(", ")||"Error desconocido");

    currentSessionId = json.session_id;
    displayResults(json.result);
    btnPdf.disabled = false;
  } catch(err){
    console.error("Fallo en cálculo:", err);
    alert("Error: " + (err?.message||err));
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

  // Interpretación textual (consenso categórico entre escalas)
  const cats = [
    String(result.framingham.category||""),
    String(result.score.category||""),
    String(result.acc_aha.category||"")
  ];

  const levelOf = (c) => {
    const s = c.toLowerCase();
    if (s.includes("muy")) return 4;         // muy alto
    if (s.includes("alto")) return 3;         // alto
    if (s.includes("intermedio")) return 2;  // intermedio (PCE)
    if (s.includes("moderado") || s.includes("limítrofe") || s.includes("limi")) return 1; // moderado/limítrofe
    return 0;                                  // bajo
  };
  const levels = cats.map(levelOf).sort((a,b)=>a-b);
  const medianLevel = levels[Math.floor(levels.length/2)];
  const labelMap = {
    0: "bajo",
    1: "moderado/limítrofe",
    2: "intermedio",
    3: "alto",
    4: "muy alto"
  };
  const globalLabel = labelMap[medianLevel];
  const dispersion = levels[levels.length-1] - levels[0];

  const catsPretty = `Framingham: ${cats[0]} · SCORE2: ${cats[1]} · ACC/AHA: ${cats[2]}`;
  const note = dispersion >= 2 ? " (discordancia alta entre escalas)" : "";
  interpretationDiv.innerHTML =
    `<p>Riesgo global (consenso): <strong>${globalLabel}</strong>${note}</p>
     <p style="margin-top:0.3rem;color:#555">Categorías por escala → ${catsPretty}</p>`;

  generateCharts(result);
}

// Perfiles predeterminados
const PRESETS = {
  bajo_h40: {
    edad: 40, sexo: "hombre", peso: 78, altura: 175,
    fumador: false, diabetes: false,
    colesterol_total: 180, hdl: 55, ldl: 110,
    presion_sistolica: 118, presion_diastolica: 76,
    tratamiento_hipertension: false, estatinas: false
  },
  moderado_m55: {
    edad: 55, sexo: "mujer", peso: 68, altura: 162,
    fumador: false, diabetes: true,
    region_riesgo: "bajo",
    colesterol_total: 220, hdl: 50, ldl: 140,
    presion_sistolica: 140, presion_diastolica: 90,
    tratamiento_hipertension: false, estatinas: false
  },
  alto_h65_fumador: {
    edad: 65, sexo: "hombre", peso: 85, altura: 172,
    fumador: true, diabetes: false,
    colesterol_total: 240, hdl: 42, ldl: 160,
    presion_sistolica: 148, presion_diastolica: 90,
    tratamiento_hipertension: true, estatinas: false
  },
  muy_alto_m70_dm_htn: {
    edad: 70, sexo: "mujer", peso: 70, altura: 160,
    fumador: true, diabetes: true,
    colesterol_total: 300, hdl: 35, ldl: 200,
    presion_sistolica: 180, presion_diastolica: 100,
    tratamiento_hipertension: true, estatinas: true
  }
};

profileSelect?.addEventListener("change", () => {
  const key = profileSelect.value;
  if (!key || !PRESETS[key]) return;
  const data = PRESETS[key];
  // Rellenar inputs
  for (const [k, v] of Object.entries(data)){
    if (!(k in form.elements)) continue;
    const el = form.elements[k];
    if (el.type === "checkbox"){
      el.checked = Boolean(v);
    } else if (el.tagName === "SELECT"){
      el.value = String(v);
    } else {
      el.value = String(v);
    }
  }
});
