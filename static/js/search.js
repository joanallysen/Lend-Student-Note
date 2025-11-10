
export function toggleFilters() {
    const filtersContent = document.getElementById('filtersContent');
    const toggleText = document.getElementById('filterToggleText');
    const toggleIcon = document.getElementById('filterToggleIcon');
    const filterHeaderText = document.getElementById('filterText')
    
    if (filtersContent.classList.contains('hidden')) {
        filtersContent.classList.remove('hidden');
        filterHeaderText.classList.remove('invisible');
        toggleText.textContent = 'Hide Filters';
        toggleIcon.style.transform = 'rotate(-90deg)';
    } else {
        filtersContent.classList.add('hidden');
        filterHeaderText.classList.add('invisible');
        toggleText.textContent = 'Show Filters';
        toggleIcon.style.transform = 'rotate(0deg)';
    }
}
 