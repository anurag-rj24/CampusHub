// CampusHub ERP - Interactive UI Engine

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initSearchFilters();
});

// Theme Management
function initTheme() {
    const savedTheme = localStorage.getItem('campushub_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('campushub_theme', next);
    updateThemeIcon(next);
}

function updateThemeIcon(theme) {
    const icon = document.getElementById('theme-icon');
    if (icon) {
        icon.textContent = theme === 'dark' ? '☀️' : '🌙';
    }
}

// Live Search & Filter for Tables
function initSearchFilters() {
    document.querySelectorAll('[data-table-search]').forEach(input => {
        const targetId = input.getAttribute('data-table-search');
        const table = document.getElementById(targetId);
        if (!table) return;

        input.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            const rows = table.querySelectorAll('tbody tr');

            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(query) ? '' : 'none';
            });
        });
    });
}

// Modal Control
function openModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
}

// Close modal on escape key or clicking outside
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal-overlay.active').forEach(m => m.classList.remove('active'));
        document.body.style.overflow = '';
    }
});

document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-overlay')) {
        e.target.classList.remove('active');
        document.body.style.overflow = '';
    }
});

// Export Table to CSV
function exportTableToCSV(tableId, filename = 'export.csv') {
    const table = document.getElementById(tableId);
    if (!table) return;

    let csv = [];
    const rows = table.querySelectorAll('tr');

    rows.forEach(row => {
        if (row.style.display === 'none') return;
        let rowData = [];
        const cols = row.querySelectorAll('th, td');
        cols.forEach(col => {
            // Ignore action buttons column if needed
            if (col.classList.contains('no-export')) return;
            let text = col.innerText.replace(/"/g, '""').trim();
            rowData.push('"' + text + '"');
        });
        csv.push(rowData.join(','));
    });

    const csvFile = new Blob([csv.join('\n')], { type: 'text/csv' });
    const downloadLink = document.createElement('a');
    downloadLink.download = filename;
    downloadLink.href = window.URL.createObjectURL(csvFile);
    downloadLink.style.display = 'none';
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
}

// AI Attendance & Bunk Safety Calculator
function calculateAttendanceSafety(attended, total, minPercentage = 75) {
    const currentPct = total === 0 ? 100 : (attended / total) * 100;
    
    if (currentPct >= minPercentage) {
        // Can miss X classes
        // (attended) / (total + X) >= minPercentage / 100
        // attended >= (total + X) * P
        // X <= (attended / P) - total
        const p = minPercentage / 100;
        const canMiss = Math.floor((attended / p) - total);
        return {
            status: 'SAFE',
            percentage: currentPct.toFixed(1),
            margin: canMiss,
            message: canMiss > 0 
                ? `You can safely skip up to ${canMiss} upcoming classes while maintaining ≥75%.`
                : `You are on the boundary! Attend the next class to stay safe.`
        };
    } else {
        // Must attend Y consecutive classes
        // (attended + Y) / (total + Y) >= minPercentage / 100
        // 100 * attended + 100 * Y >= P * total + P * Y
        // Y * (100 - P) >= P * total - 100 * attended
        const p = minPercentage;
        const needed = Math.ceil((p * total - 100 * attended) / (100 - p));
        return {
            status: 'SHORTAGE',
            percentage: currentPct.toFixed(1),
            margin: needed,
            message: `⚠️ Shortage Alert! You must attend ${needed} consecutive classes to reach 75%.`
        };
    }
}
