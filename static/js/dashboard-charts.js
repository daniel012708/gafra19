document.addEventListener('DOMContentLoaded', function() {
  try {
    // Activity Chart (line) using ventas data from template
    const ventasLabelsEl = document.getElementById('ventas-labels');
    const ventasDataEl = document.getElementById('ventas-data');
    const ventasLabels = ventasLabelsEl ? JSON.parse(ventasLabelsEl.textContent) : [];
    const ventasData = ventasDataEl ? JSON.parse(ventasDataEl.textContent) : [];
    const activityCtx = document.getElementById('activityChart');
    if (activityCtx && ventasLabels.length) {
      new Chart(activityCtx, {
        type: 'line',
        data: {
          labels: ventasLabels,
          datasets: [{
            label: 'Ventas',
            data: ventasData,
            borderColor: getComputedStyle(document.documentElement).getPropertyValue('--color-primary') || '#6366F1',
            backgroundColor: 'rgba(99,102,241,0.08)',
            tension: 0.36,
            fill: true,
            pointRadius: 3
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: { y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.04)' } }, x: { grid: { color: 'rgba(0,0,0,0.02)' } } },
          interaction: { intersect: false, mode: 'index' }
        }
      });
    }

    // Products bar chart
    const productosLabelsEl = document.getElementById('productos-labels');
    const productosDataEl = document.getElementById('productos-data');
    const productosLabels = productosLabelsEl ? JSON.parse(productosLabelsEl.textContent) : [];
    const productosValues = productosDataEl ? JSON.parse(productosDataEl.textContent) : [];
    const productosCtx = document.getElementById('productosBar');
    if (productosCtx && productosLabels.length) {
      new Chart(productosCtx, {
        type: 'bar',
        data: { labels: productosLabels, datasets: [{ label: 'Unidades vendidas', data: productosValues, backgroundColor: productosLabels.map((_,i)=>['#6366F1','#06B6D4','#43e97b','#fa709a','#f093fb','#2c3e50'][i%6]) }]},
        options: { responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}}, scales:{ y:{ beginAtZero:true } } }
      });
    }

    // Categories pie/doughnut
    const categoriasLabelsEl = document.getElementById('categorias-labels');
    const categoriasDataEl = document.getElementById('categorias-data');
    const categoriasLabels = categoriasLabelsEl ? JSON.parse(categoriasLabelsEl.textContent) : [];
    const categoriasValues = categoriasDataEl ? JSON.parse(categoriasDataEl.textContent) : [];
    const categoriasCtx = document.getElementById('categoriasPie');
    if (categoriasCtx && categoriasLabels.length) {
      new Chart(categoriasCtx, {
        type: 'doughnut',
        data: { labels: categoriasLabels, datasets: [{ data: categoriasValues, backgroundColor: ['#6366F1','#06B6D4','#43e97b','#fa709a','#f093fb','#2c3e50'] }]},
        options: { responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'bottom'}} }
      });
    }

    // Stats doughnut (hidden data -> stats-data)
    const statsDataEl = document.getElementById('stats-data');
    const statsData = statsDataEl ? JSON.parse(statsDataEl.textContent) : null;
    const statsCtx = document.getElementById('statsChart');
    if (statsCtx && statsData) {
      new Chart(statsCtx, {
        type: 'doughnut',
        data: {
          labels: ['Proveedores', 'Productos', 'Materias Primas', 'Clientes', 'Ventas', 'Producción'],
          datasets: [{
            data: statsData,
            backgroundColor: ['#6366F1','#06B6D4','#43e97b','#fa709a','#f093fb','#2c3e50'],
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'bottom', labels: { padding: 12, usePointStyle: true } } }
        }
      });
    }

    // Summary donut in quick actions
    const summaryDonutEl = document.getElementById('summaryDonut');
    if (summaryDonutEl && statsData) {
      new Chart(summaryDonutEl, {
        type: 'doughnut',
        data: {
          labels: ['Proveedores','Productos','Materias','Clientes','Ventas','Producción'],
          datasets: [{ data: statsData, backgroundColor:['#6366F1','#06B6D4','#43e97b','#fa709a','#f093fb','#2c3e50'] }]
        },
        options: { responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}} }
      });
    }

    // mini-sparklines removed per UI request (KPI cards now horizontal)
  } catch (e) {
    console && console.debug && console.debug(e);
  }
});
