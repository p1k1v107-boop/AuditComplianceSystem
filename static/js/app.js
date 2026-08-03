document.addEventListener('DOMContentLoaded', () => {
    // --- Sidebar Toggle ---
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
        
        // Tutup sidebar jika klik di luar pada mobile
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 768) {
                if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target) && sidebar.classList.contains('open')) {
                    sidebar.classList.remove('open');
                }
            }
        });
    }

    // --- Donut Chart (CSS Conic Gradient) ---
    const donutChart = document.getElementById('donutChart');
    if (donutChart) {
        const minor = parseInt(donutChart.dataset.minor) || 0;
        const mayor = parseInt(donutChart.dataset.mayor) || 0;
        const kritis = parseInt(donutChart.dataset.kritis) || 0;
        const total = minor + mayor + kritis;
        
        if (total > 0) {
            const pMinor = (minor / total) * 100;
            const pMayor = (mayor / total) * 100;
            const pKritis = (kritis / total) * 100;
            
            // #10b981 (green), #f59e0b (yellow), #ef4444 (red)
            donutChart.style.background = `conic-gradient(
                #10b981 0% ${pMinor}%,
                #f59e0b ${pMinor}% ${pMinor + pMayor}%,
                #ef4444 ${pMinor + pMayor}% 100%
            )`;
        } else {
            donutChart.style.background = 'var(--bg-primary)';
        }
        
        // Inner circle for donut effect
        const innerCircle = document.createElement('div');
        innerCircle.style.width = '70%';
        innerCircle.style.height = '70%';
        innerCircle.style.background = 'var(--bg-card)';
        innerCircle.style.borderRadius = '50%';
        innerCircle.style.margin = '15%';
        donutChart.appendChild(innerCircle);
    }
    
    // --- Auto-hide alerts ---
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000); // 5 detik
    });

    // --- Set Bar Widths ---
    const barFills = document.querySelectorAll('.bar-fill');
    barFills.forEach(bar => {
        const width = bar.getAttribute('data-width');
        if (width !== null) {
            bar.style.width = width + '%';
        }
    });
});
