document.addEventListener("DOMContentLoaded", function () {
    const selects = document.querySelectorAll('.searchable-dropdown');

    selects.forEach(select => {
        //When items are added to the select, update the dropdown
        const observer = new MutationObserver(() => {
            searchInput.value = 'Search...';
            populateOptions();
        });
        observer.observe(select, {childList: true});
        // Wrap the <select> in a custom dropdown structure
        const wrapper = document.createElement('div');
        wrapper.className = 'dropdown-wrapper';
        select.parentNode.insertBefore(wrapper, select);
        wrapper.appendChild(select);

        // Hide the native select dropdown
        select.style.display = 'none';

        // Create a custom dropdown container
        const dropdownContainer = document.createElement('div');
        dropdownContainer.className = 'custom-dropdown';
        wrapper.appendChild(dropdownContainer);

        // Add a search input
        const searchInput = document.createElement('input');
        searchInput.className = 'dropdown-search';
        searchInput.type = 'text';
        searchInput.placeholder = 'Search...';
        dropdownContainer.appendChild(searchInput);

        // Create a custom dropdown options list
        const optionsList = document.createElement('ul');
        optionsList.className = 'options-list';
        dropdownContainer.appendChild(optionsList);

        // Populate options list
        const populateOptions = () => {
            optionsList.innerHTML = ''; // Clear previous options
            Array.from(select.options).forEach(option => {
                //console.log(option);
                const listItem = document.createElement('li');
                listItem.textContent = option.textContent;
                listItem.dataset.value = option.value;
                listItem.className = 'option-item';
                optionsList.appendChild(listItem);

                // Select the option on click
                listItem.addEventListener('click', (event) => {
                    event.stopPropagation(); // Prevent dropdown closing
                    select.value = option.value;
                    searchInput.value = option.textContent; // Show selected value
                    select.dispatchEvent(new Event('change')); // Trigger change event
                    dropdownContainer.classList.remove('open');
                });
            });
        };
        populateOptions();

        // Filter options based on input
        searchInput.addEventListener('input', () => {
            const filter = searchInput.value.toLowerCase();
            const optionItems = optionsList.querySelectorAll('.option-item');
            optionItems.forEach(item => {
                const text = item.textContent.toLowerCase();
                item.style.display = text.includes(filter) ? '' : 'none';
            });
        });

        // Toggle dropdown visibility
        dropdownContainer.addEventListener('click', (event) => {
            event.stopPropagation(); // Prevent event bubbling
            dropdownContainer.classList.toggle('open');
            searchInput.focus();
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (event) => {
            if (!wrapper.contains(event.target)) {
                dropdownContainer.classList.remove('open');
            }
        });
    });
});


function toggleMenu() {
    document.getElementById("hamburgerMenu").classList.toggle("open");
}

// Get the toggle checkbox element
const darkModeCheckbox = document.getElementById('darkModeCheckbox');

// Check if dark mode was previously enabled and apply it
if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-mode');
    darkModeCheckbox.checked = true;
}

// Add event listener for the dark mode toggle
darkModeCheckbox.addEventListener('change', () => {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
});