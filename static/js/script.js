document.addEventListener('DOMContentLoaded', event => {

    // Toggle Sidebar
    const sidebarToggle = document.body.querySelector('#sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', event => {
            event.preventDefault();
            document.body.classList.toggle('sb-sidenav-toggled');
            localStorage.setItem('sb|sidebar-toggle', document.body.classList.contains('sb-sidenav-toggled'));
        });
    }

    // Theme Toggling
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const htmlElement = document.documentElement;

    // Check local storage for theme preference
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = htmlElement.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            setTheme(newTheme);
        });
    }

    function setTheme(theme) {
        htmlElement.setAttribute('data-bs-theme', theme);
        localStorage.setItem('theme', theme);

        // Update Icon
        if (theme === 'dark') {
            themeIcon.classList.remove('bi-moon-stars-fill');
            themeIcon.classList.add('bi-sun-fill');
        } else {
            themeIcon.classList.remove('bi-sun-fill');
            themeIcon.classList.add('bi-moon-stars-fill');
        }
    }

    // Sidebar Menu Persistence
    // Keep Master Data menu always open
    const masterDataMenu = document.getElementById('masterDataMenu');
    const masterDataToggle = document.querySelector('[data-bs-target="#masterDataMenu"]');

    if (masterDataMenu && masterDataToggle) {
        // Always show Master Data menu
        masterDataMenu.classList.add('show');
        masterDataToggle.setAttribute('aria-expanded', 'true');

        // Store all collapse states
        const collapseElements = document.querySelectorAll('.collapse');
        collapseElements.forEach(collapse => {
            collapse.addEventListener('shown.bs.collapse', function () {
                localStorage.setItem('collapse_' + this.id, 'open');
            });

            collapse.addEventListener('hidden.bs.collapse', function () {
                localStorage.setItem('collapse_' + this.id, 'closed');
            });

            // Restore state from localStorage
            const savedState = localStorage.getItem('collapse_' + collapse.id);
            if (savedState === 'open' && !collapse.classList.contains('show')) {
                const bsCollapse = new bootstrap.Collapse(collapse, { toggle: false });
                bsCollapse.show();
            }
        });
    }

});
