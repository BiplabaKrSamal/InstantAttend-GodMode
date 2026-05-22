/**
 * InstantAttend God Mode — Dashboard JS
 * Handles: Chart.js weekly bar, Socket.IO live updates, toast notifications
 */

document.addEventListener('DOMContentLoaded', () => {

  /* ── Weekly Attendance Chart ───────────────────────────── */
  const chartEl = document.getElementById('weeklyChart');
  if (chartEl && typeof weeklyData !== 'undefined') {
    new Chart(chartEl, {
      type: 'bar',
      data: {
        labels: weeklyData.map(d => d.date.slice(5)),
        datasets: [{
          label: 'Present',
          data: weeklyData.map(d => d.count),
          backgroundColor: 'rgba(99, 102, 241, 0.6)',
          borderColor: '#6366f1',
          borderWidth: 2,
          borderRadius: 6,
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: '#2d2d4e' }, ticks: { color: '#94a3b8' } },
          y: { grid: { color: '#2d2d4e' }, ticks: { color: '#94a3b8', stepSize: 1 } }
        }
      }
    });
  }

  /* ── Socket.IO Live Updates ────────────────────────────── */
  if (typeof io !== 'undefined') {
    const socket = io();
    let rowCount = document.querySelectorAll('#attendance-body tr').length;

    socket.on('attendance_update', data => {
      // Remove empty state row if present
      const empty = document.getElementById('empty-row');
      if (empty) empty.remove();

      // Prepend new row
      rowCount++;
      const tbody = document.getElementById('attendance-body');
      if (!tbody) return;

      const tr = document.createElement('tr');
      tr.classList.add('row-flash');
      tr.innerHTML = `
        <td style="color:var(--muted)">${rowCount}</td>
        <td><i class="fa-solid fa-circle-user me-2" style="color:#6366f1"></i>${data.name}</td>
        <td><code style="color:#a78bfa">${data.roll}</code></td>
        <td><i class="fa-regular fa-clock me-1" style="color:var(--muted)"></i>${data.time}</td>
        <td><span class="badge-present">Present</span></td>
      `;
      tbody.prepend(tr);

      // Update stat counter
      const stat = document.getElementById('stat-present');
      if (stat) stat.textContent = parseInt(stat.textContent) + 1;

      // Show toast
      showToast(`${data.name} marked present at ${data.time}`);
    });

    socket.on('connect_error', () => {
      console.warn('InstantAttend: WebSocket connection lost. Retrying...');
    });
  }

  /* ── Toast Helper ──────────────────────────────────────── */
  function showToast(message) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = 'live-toast';
    toast.innerHTML = `
      <i class="fa-solid fa-check-circle me-2" style="color:#10b981"></i>
      <strong>${message}</strong>
    `;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
  }

  /* ── Confirm delete buttons ────────────────────────────── */
  document.querySelectorAll('.confirm-delete').forEach(form => {
    form.addEventListener('submit', e => {
      const name = form.dataset.name || 'this user';
      if (!confirm(`Delete ${name}? This will remove all their face data and attendance records.`)) {
        e.preventDefault();
      }
    });
  });

});
