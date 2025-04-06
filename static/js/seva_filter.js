// JavaScript for Seva filtering
document.addEventListener('DOMContentLoaded', function() {
    // Function to filter sevas
    window.filterSevas = function() {
        var selectedType = document.getElementById("sevaType").value;
        var sevaCards = document.querySelectorAll('.seva-card');
        var visibleCount = 0;
        
        // Client-side filtering
        sevaCards.forEach(function(card) {
            var sevaType = card.querySelector('.seva-type-badge').innerText;
            
            if (selectedType === 'all' || sevaType === selectedType) {
                card.style.display = '';
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });
        
        // Update the counter
        var sevaCountElement = document.querySelector('.seva-count');
        if (sevaCountElement) {
            sevaCountElement.innerText = visibleCount + ' sevas found';
        }
        
        // Log to console for debugging
        console.log('Client-side filter applied:', selectedType, 'Visible sevas:', visibleCount);
        
        return false; // Prevent form submission
    };
    
    // Initialize the filter
    var sevaTypeSelect = document.getElementById("sevaType");
    if (sevaTypeSelect) {
        // Set the initial count
        var visibleSevas = document.querySelectorAll('.seva-card').length;
        var sevaCountElement = document.querySelector('.seva-count');
        if (sevaCountElement) {
            sevaCountElement.innerText = visibleSevas + ' sevas found';
        }
        
        // Ensure the onchange attribute is set
        if (sevaTypeSelect.getAttribute('onchange') !== 'filterSevas()') {
            sevaTypeSelect.setAttribute('onchange', 'filterSevas(); return false;');
        }
    }
}); 