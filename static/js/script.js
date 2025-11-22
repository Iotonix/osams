document.addEventListener('DOMContentLoaded', event => {

    // --- 1. Sidebar Toggle Logic ---
    const sidebarToggle = document.body.querySelector('#sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', event => {
            event.preventDefault();
            document.body.classList.toggle('sb-sidenav-toggled');
            localStorage.setItem('sb|sidebar-toggle', document.body.classList.contains('sb-sidenav-toggled'));
        });
    }

    // Restore Sidebar Toggle State
    const sidebarState = localStorage.getItem('sb|sidebar-toggle');
    if (sidebarState === 'true') {
        document.body.classList.add('sb-sidenav-toggled');
    }


    // --- 2. Theme Toggling Logic ---
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
        if (themeIcon) {
            if (theme === 'dark') {
                themeIcon.classList.remove('bi-moon-stars-fill');
                themeIcon.classList.add('bi-sun-fill');
            } else {
                themeIcon.classList.remove('bi-sun-fill');
                themeIcon.classList.add('bi-moon-stars-fill');
            }
        }
    }


    // --- 3. Modern Active State & Menu Persistence ---
    const currentPath = window.location.pathname;

    // Select only our specific sidebar links (avoids conflicts)
    const sidebarLinks = document.querySelectorAll('.sidebar-link');

    sidebarLinks.forEach(link => {
        const linkHref = link.getAttribute('href');

        // Compare path (exact match)
        if (linkHref === currentPath) {
            // 1. Highlight the link
            link.classList.add('active');

            // 2. If it's inside a submenu, open the parent
            const parentSubmenu = link.closest('.submenu');
            if (parentSubmenu) {
                // Show the UL
                parentSubmenu.classList.add('show');

                // Highlight and Expand the Parent Toggle Button
                const submenuId = parentSubmenu.getAttribute('id');
                const parentToggle = document.querySelector(`[href="#${submenuId}"]`);

                if (parentToggle) {
                    parentToggle.classList.add('active'); // Optional: highlight parent too
                    parentToggle.classList.remove('collapsed');
                    parentToggle.setAttribute('aria-expanded', 'true');
                }
            }
        }
    });

    // --- 4. Manual Persistence (Optional / Extra Robustness) ---
    // Save state of collapsed menus to localStorage so they stay open on refresh
    const collapses = document.querySelectorAll('.sidebar-link[data-bs-toggle="collapse"]');
    collapses.forEach(toggle => {
        toggle.addEventListener('click', function () {
            const targetId = this.getAttribute('href'); // e.g. #masterDataMenu
            // We wait a tiny bit for the class to update
            setTimeout(() => {
                const isExpanded = this.getAttribute('aria-expanded') === 'true';
                localStorage.setItem('menu_state_' + targetId, isExpanded);
            }, 50);
        });

        // Restore state on load
        const targetId = toggle.getAttribute('href');
        const wasExpanded = localStorage.getItem('menu_state_' + targetId) === 'true';

        // Only force open if it wasn't already opened by the "Active State" logic above
        if (wasExpanded) {
            const targetMenu = document.querySelector(targetId);
            if (targetMenu && !targetMenu.classList.contains('show')) {
                targetMenu.classList.add('show');
                toggle.classList.remove('collapsed');
                toggle.setAttribute('aria-expanded', 'true');
            }
        }
    });

});