// Mendapatkan halaman saat ini dari URL
const urlParams = new URLSearchParams(window.location.search);
const currentPage = urlParams.get('page') || 1;

// Menambahkan kelas 'active' pada halaman yang sesuai
const activePage = document.getElementById(`page-${currentPage}`);
if (activePage) {
    activePage.classList.add('active');
}

function validateSearch() {
    const searchInput = document.querySelector('input[name="q"]');
    const searchWrapper = document.querySelector('.search-box-wrapper');
    const errorDiv = document.getElementById('searchError');

    const searchValue = searchInput.value.trim();

    if (!searchValue) {
        // Tambahkan class error ke wrapper
        searchWrapper.classList.add('error');

        // Focus input and add shake effect
        searchInput.focus();
        searchInput.classList.add('shake');
        searchInput.classList.add('error-highlight');

        // Remove shake class after animation
        setTimeout(() => {
            searchInput.classList.remove('shake');
        }, 500);

        // Remove error classes after delay
        setTimeout(() => {
            searchInput.classList.remove('error-highlight');
            searchWrapper.classList.remove('error');
        }, 3000);

        return false;
    }

    return true;
}


// Event listener untuk input
const searchInput = document.querySelector('input[name="q"]');
if (searchInput) {
    // Hapus error state ketika user mulai mengetik
    searchInput.addEventListener('input', function () {
        const errorDiv = document.getElementById('searchError');
        const searchWrapper = document.querySelector('.search-box-wrapper');

        if (errorDiv.classList.contains('show')) {
            // Hapus semua error states
            errorDiv.classList.remove('show');
            this.classList.remove('error-highlight');
            searchWrapper.classList.remove('error');
            errorDiv.style.visibility = 'hidden';
        }
    });

    // Hapus error highlight saat focus hilang
    searchInput.addEventListener('blur', function () {
        if (!this.value.trim()) {
            this.classList.remove('error-highlight');
            document.querySelector('.search-box-wrapper').classList.remove('error');
        }
    });
}

// Validasi untuk tombol submit
document.querySelectorAll('button[type="submit"]').forEach(button => {
    button.addEventListener('click', function (e) {
        const searchInput = document.querySelector('input[name="q"]');

        // Tambahkan class error-highlight sebelum validasi
        if (!searchInput.value.trim()) {
            searchInput.classList.add('error-highlight');
        }

        if (!validateSearch()) {
            e.preventDefault();
        }
    });
});

