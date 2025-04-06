/**
 * Navigation Stability Script
 * 
 * This script ensures the navigation menu correctly highlights the active page
 * even when pages are loaded outside the template system or when templates
 * don't properly set active classes.
 */
document.addEventListener('DOMContentLoaded', function() {
    // Get current page path
    const path = window.location.pathname;
    
    // Select all nav links
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    // Skip if we already have an active link (set by the template)
    const hasActiveLink = Array.from(navLinks).some(link => link.classList.contains('active'));
    if (hasActiveLink) return;
    
    // If no active links were set by the server, apply client-side logic
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        
        // Special case for home page
        if (path === '/' && href === '/') {
            link.classList.add('active');
            return;
        }
        
        // Handle subpaths and exact matches
        if (path !== '/' && href !== '/') {
            // Check if this is an exact match
            if (path === href) {
                link.classList.add('active');
                return;
            }
            
            // Check for subpaths but only if the href is not just '/'
            if (href.length > 1 && path.startsWith(href)) {
                // Ensure we're matching at a path boundary
                // e.g., '/events' should match '/events/123' but not '/events-calendar'
                if (path === href || path.charAt(href.length) === '/') {
                    link.classList.add('active');
                }
            }
        }
    });
}); 