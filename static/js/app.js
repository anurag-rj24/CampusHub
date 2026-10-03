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

// Sidebar State & Toggle
function initSidebar() {
    const isCollapsed = localStorage.getItem('campushub_sidebar_collapsed') === 'true';
    const appContainer = document.getElementById('appContainer');
    if (appContainer && isCollapsed && window.innerWidth > 1024) {
        appContainer.classList.add('sidebar-collapsed');
    }
}

function toggleSidebar() {
    const appContainer = document.getElementById('appContainer');
    const sidebar = document.getElementById('mainSidebar');
    if (!appContainer) return;

    if (window.innerWidth <= 1024) {
        // Mobile Drawer Toggle
        if (sidebar) {
            sidebar.classList.toggle('mobile-open');
        }
        const backdrop = document.getElementById('sidebarBackdrop');
        if (backdrop) {
            backdrop.classList.toggle('active');
        }
    } else {
        // Desktop Full Width Collapse
        const isCollapsed = appContainer.classList.toggle('sidebar-collapsed');
        localStorage.setItem('campushub_sidebar_collapsed', isCollapsed);
    }

    // Trigger chart resize if charts are present
    setTimeout(() => {
        window.dispatchEvent(new Event('resize'));
    }, 350);
}

// Interactive Dashboard Content Tabs Switcher (News, Videos, Gallery, Events)
function switchContentTab(tabName, btnElement) {
    // Update active button
    const container = btnElement.closest('.content-tab-bar') || btnElement.parentElement;
    if (container) {
        container.querySelectorAll('.tab-btn').forEach(b => {
            b.classList.remove('btn-primary');
            b.classList.add('btn-secondary');
        });
        btnElement.classList.remove('btn-secondary');
        btnElement.classList.add('btn-primary');
    }

    // Hide all tab panels
    document.querySelectorAll('.content-tab-panel').forEach(panel => {
        panel.classList.remove('active');
    });

    // Show selected panel
    const targetPanel = document.getElementById('panel-' + tabName);
    if (targetPanel) {
        targetPanel.classList.add('active');
    }
}

// Category filter for gallery / videos / events
function filterGalleryItems(category, btnElement) {
    if (btnElement && btnElement.parentElement) {
        btnElement.parentElement.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
        btnElement.classList.add('active');
    }

    document.querySelectorAll('.gallery-item').forEach(item => {
        const itemCat = item.getAttribute('data-category');
        if (category === 'all' || itemCat === category) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
}

function filterVideoItems(category, btnElement) {
    if (btnElement && btnElement.parentElement) {
        btnElement.parentElement.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
        btnElement.classList.add('active');
    }

    document.querySelectorAll('.video-card-item').forEach(item => {
        const itemCat = item.getAttribute('data-category');
        if (category === 'all' || itemCat === category) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
}

// Play Video Modal Demo
function playLectureVideo(title, speaker, duration) {
    const modalTitle = document.getElementById('videoModalTitle');
    const modalSpeaker = document.getElementById('videoModalSpeaker');
    if (modalTitle) modalTitle.textContent = title;
    if (modalSpeaker) modalSpeaker.textContent = speaker + ' • Duration: ' + duration;
    openModal('videoPlayerModal');
}

// Lightbox preview for gallery
function openGalleryLightbox(title, tag, imgSrc) {
    const lightboxTitle = document.getElementById('lightboxTitle');
    const lightboxTag = document.getElementById('lightboxTag');
    const lightboxImg = document.getElementById('lightboxImg');
    if (lightboxTitle) lightboxTitle.textContent = title;
    if (lightboxTag) lightboxTag.textContent = tag;
    if (lightboxImg) lightboxImg.src = imgSrc;
    openModal('galleryLightboxModal');
}

// Auto init sidebar on load
document.addEventListener('DOMContentLoaded', () => {
    initSidebar();
});
