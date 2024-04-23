var themeToggleDarkIcon = document.getElementById('theme-toggle-dark-icon');
var themeToggleLightIcon = document.getElementById('theme-toggle-light-icon');
var themeToggleBtn = document.getElementById('theme-toggle');

// Set initial theme based on localStorage or user's preference
if (localStorage.getItem('color-theme') === 'dark' || (!localStorage.getItem('color-theme') && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    enableDarkMode();
} else {
    disableDarkMode();
}

// Toggle theme mode and update localStorage
themeToggleBtn.addEventListener('click', function() {
    if (document.documentElement.classList.contains('dark')) {
        disableDarkMode();
    } else {
        enableDarkMode();
    }
});

function enableDarkMode() {
    document.documentElement.classList.add('dark');
    localStorage.setItem('color-theme', 'dark');
    themeToggleDarkIcon.classList.add('hidden');
    themeToggleLightIcon.classList.remove('hidden');
}

function disableDarkMode() {
    document.documentElement.classList.remove('dark');
    localStorage.setItem('color-theme', 'light');
    themeToggleDarkIcon.classList.remove('hidden');
    themeToggleLightIcon.classList.add('hidden');
}
