// Dashboard chart initialization moved to external file to satisfy CSP
window.addEventListener('DOMContentLoaded', function () {
  const canvasEl = document.getElementById('donationsByMonth');
  const errorEl = document.getElementById('chartError');

  function showError(msg) {
    if (!errorEl) return;
    errorEl.textContent = msg;
    errorEl.classList.remove('d-none');
  }

  if (!canvasEl) {
    console.error('Canvas not found');
    showError('Erreur : Canvas introuvable.');
    return;
  }

  // Ensure visible height
  canvasEl.style.height = '300px';

  let labels = [];
  let data = [];
  try {
    labels = JSON.parse(canvasEl.dataset.labels || '[]');
    data = JSON.parse(canvasEl.dataset.values || '[]');
  } catch (e) {
    console.error('Error parsing chart data', e);
    showError("Erreur : Impossible d'analyser les données du graphique.");
    return;
  }

  function initChart() {
    const ctx = canvasEl.getContext('2d');
    if (!ctx) { console.error('2D context not available'); showError('Erreur : Contexte 2D indisponible.'); return; }

    if (!Array.isArray(labels) || !Array.isArray(data)) {
      showError('Erreur : Données du graphique invalides.');
      return;
    }

    // If all values are zero, display a friendly message
    if (data.length === 0 || data.every(v => Number(v) === 0)) {
      showError("Aucune donnée disponible pour l'année courante.");
      return;
    }

    // Custom HSL palette for bars
    const barColors = labels.map((_, idx) => `hsl(${(idx * 30) % 360} 55% 45% / 0.70)`);
    const barBorders = labels.map((_, idx) => `hsl(${(idx * 30) % 360} 65% 35% / 1)`);

    try {
      new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [
            { type: 'bar', label: 'Montant des dons (€)', data: data, backgroundColor: barColors, borderColor: barBorders, borderWidth: 1 },
            { type: 'line', label: 'Tendance des dons', data: data, borderColor: '#2c5530', pointBackgroundColor: '#2c5530', pointRadius: 3, tension: 0.3, fill: false }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: { y: { beginAtZero: true, ticks: { callback: (v) => v + ' €' } } },
          plugins: { legend: { display: true, position: 'top' }, tooltip: { callbacks: { label: (ctx) => ctx.parsed.y + ' €' } } }
        }
      });
      console.log('Chart initialized successfully');
    } catch (error) {
      console.error('Error initializing chart:', error);
      showError("Erreur d'initialisation du graphique : " + error.message);
    }
  }

  if (typeof Chart === 'undefined') {
    console.warn('Chart.js not found locally, loading from CDN...');
    const s = document.createElement('script');
    s.src = 'https://cdn.jsdelivr.net/npm/chart.js';
    s.onload = initChart;
    s.onerror = function () { showError('Erreur : Impossible de charger Chart.js (local et CDN).'); };
    document.head.appendChild(s);
  } else {
    initChart();
  }
});
