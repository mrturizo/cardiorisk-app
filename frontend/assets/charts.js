/* Generación de gráficos con Chart.js */
function generateCharts(result){
  const container = document.getElementById("charts");
  container.innerHTML = `<canvas id="barChart"></canvas>`;
  const ctx = document.getElementById("barChart").getContext("2d");
  const labelsBase = ["Framingham","SCORE","ACC/AHA"];
  const categories = [
    result.framingham.category,
    result.score.category,
    result.acc_aha.category
  ];
  const labels = labelsBase.map((name, i) => `${name} (${categories[i]})`);

  const values = [
    result.framingham.percent,
    result.score.percent,
    result.acc_aha.percent
  ];

  const colorFor = (cat) => {
    const c = String(cat || "").toLowerCase();
    if (c.includes("muy")) return "#b71c1c";      // muy alto
    if (c.includes("alto")) return "#C62828";     // alto
    if (c.includes("intermedio")) return "#F9A825"; // intermedio (PCE)
    if (c.includes("limítrofe") || c.includes("limi")) return "#F9A825";
    if (c.includes("moderado")) return "#F9A825"; // por compatibilidad
    return "#2E7D32"; // bajo
  };

  const data = {
    labels,
    datasets:[{
      label:"Riesgo (%)",
      data: values,
      backgroundColor: categories.map(colorFor)
    }]
  };
  new Chart(ctx,{
    type:"bar",
    data,
    options:{
      responsive:true,
      plugins:{
        tooltip:{
          callbacks:{
            label:(ctx)=>{
              const cat = categories[ctx.dataIndex];
              const v = ctx.parsed.y;
              return `Riesgo: ${v}% — ${cat}`;
            }
          }
        }
      },
      scales:{
        y:{
          beginAtZero:true,
          suggestedMax: 40,
          ticks:{
            callback:(v)=>`${v}%`
          }
        }
      }
    }
  });
}
