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
    const masterDataToggle = document.querySelector('[href="#masterDataMenu"]');

    if (masterDataMenu && masterDataToggle) {
        // Force Master Data menu to stay open
        masterDataMenu.classList.add('show');
        masterDataToggle.setAttribute('aria-expanded', 'true');
        masterDataToggle.classList.remove('collapsed');

        // Prevent Master Data menu from collapsing
        masterDataToggle.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        });

        // Store all collapse states for other menus
        const collapseElements = document.querySelectorAll('.collapse');
        collapseElements.forEach(collapse => {
            if (collapse.id !== 'masterDataMenu') {
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
            }
        });
    }

    // Fix active state - only highlight current page in submenu
    const currentPath = window.location.pathname;
    const sidebarLinks = document.querySelectorAll('#sidebar-wrapper .sidebar-submenu a');

    // Remove active from ALL submenu links first
    sidebarLinks.forEach(link => {
        link.classList.remove('active');
    });

    // Add active only to the exact matching link
    sidebarLinks.forEach(link => {
        const linkHref = link.getAttribute('href');
        if (linkHref === currentPath) {
            link.classList.add('active');
        }
    });

});