const search_icon = document.getElementById('search-btn');
const search_bar = document.getElementById('container-input');

search_icon.addEventListener('click', (event) => {
    event.stopPropagation(); // Prevent propagation to the document
    search_icon.classList.add('hidden');
    search_bar.classList.remove('hidden');
});

// Add an event listener to the document
document.addEventListener('click', (event) => {
    if (event.target !== search_bar && !search_bar.contains(event.target)) {
        search_icon.classList.remove('hidden');
        search_bar.classList.add('hidden');
    }
});

// Add focus and blur event listeners to the input field
const inputField = search_bar.querySelector('input');
inputField.addEventListener('focus', () => {
    search_icon.classList.add('hidden');
    search_bar.classList.remove('hidden');
});

inputField.addEventListener('blur', () => {
    // Add a short delay to handle the click event on the search icon
    setTimeout(() => {
        if (!search_bar.contains(document.activeElement)) {
            search_icon.classList.remove('hidden');
            search_bar.classList.add('hidden');
        }
    }, 100);
});
