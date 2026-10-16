function formatNumber(value) {
  return Number(value || 0).toLocaleString();
}
function plotLayout(layout) {
  return Object.assign({
    autosize: true,
    margin: {l: 42, r: 18, t: 12, b: 42},
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    font: {family: "DM Sans, sans-serif", color: "#7c879b", size: 10},
    xaxis: {gridcolor: "#eef1f6", zerolinecolor: "#eef1f6"},
    yaxis: {gridcolor: "#eef1f6", zerolinecolor: "#eef1f6"}
  }, layout || {});
}
function renderChart(id, chart) {
  const data = chart.data || [];
  const layout = plotLayout(chart.layout || {});
  Plotly.newPlot(id, data, layout, {responsive: true, displayModeBar: false});
}
async function refreshDashboard() {
  try {
    const response = await fetch("/api/dashboard");
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Could not load dashboard.");
    document.getElementById("visitors").textContent = formatNumber(data.kpis.visitors);
    document.getElementById("page_views").textContent = formatNumber(data.kpis.page_views);
    document.getElementById("engagements").textContent = formatNumber(data.kpis.engagements);
    document.getElementById("engagement_rate").textContent = data.kpis.engagement_rate + "%";
    document.getElementById("clicks").textContent = formatNumber(data.kpis.clicks);
    document.getElementById("conversions").textContent = formatNumber(data.kpis.conversions);
    document.getElementById("ctr").textContent = data.kpis.ctr + "%";
    renderChart("trafficChart", data.traffic_chart);
    renderChart("platformChart", data.platform_chart);
    renderChart("campaignChart", data.campaign_chart);
    const tbody = document.getElementById("topPosts");
    tbody.innerHTML = "";
    if (!data.top_posts.length) {
      tbody.innerHTML = '<tr><td colspan="4">No records found.</td></tr>';
    } else {
      data.top_posts.forEach(row => {
        const tr = document.createElement("tr");
        [row.date, row.platform, row.campaign, formatNumber(row.engagements)].forEach(value => {
          const td = document.createElement("td");
          td.textContent = value ?? "";
          tr.appendChild(td);
        });
        tbody.appendChild(tr);
      });
    }
  } catch (error) {
    console.error(error);
    document.getElementById("uploadMessage").textContent = "Dashboard could not load. Please refresh the page.";
    document.getElementById("uploadMessage").className = "message error";
  }
}
document.getElementById("uploadForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const input = document.getElementById("csvFile");
  const message = document.getElementById("uploadMessage");
  if (!input.files.length) return;
  const formData = new FormData();
  formData.append("file", input.files[0]);
  message.textContent = "Uploading and processing CSV…";
  message.className = "message";
  try {
    const response = await fetch("/upload", {method: "POST", body: formData});
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Upload failed.");
    message.textContent = result.message;
    message.className = "message success";
    await refreshDashboard();
  } catch (error) {
    message.textContent = error.message;
    message.className = "message error";
  }
});
window.addEventListener("DOMContentLoaded", refreshDashboard);
