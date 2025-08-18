/* Generación de gráficos con Chart.js */
function generateCharts(result){
  const container = document.getElementById("charts");
  container.innerHTML = `<canvas id="barChart"></canvas>`;
  const ctx = document.getElementById("barChart").getContext("2d");
  const data = {
    labels: ["Framingham","SCORE","ACC/AHA"],
    datasets:[{
      label:"Riesgo (%)",
      data:[
        result.framingham.percent,
        result.score.percent,
        result.acc_aha.percent
      ],
      backgroundColor:["#2E7D32","#F9A825","#C62828"]
    }]
  };
  new Chart(ctx,{type:"bar",data});
}
