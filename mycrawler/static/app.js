let items = document.querySelectorAll('.slider .list .item');
let next = document.getElementById('next');
let prev = document.getElementById('prev');
let thumbnails = document.querySelectorAll('.thumbnail .item');

let itemActive = 0;
let countItem = items.length;

// Fungsi untuk menampilkan slider aktif
function showSlider() {
    // Hapus kelas 'active' dari item dan thumbnail sebelumnya
    document.querySelector('.slider .list .item.active').classList.remove('active');
    document.querySelector('.thumbnail .item.active').classList.remove('active');

    // Tambahkan kelas 'active' ke item dan thumbnail yang baru
    items[itemActive].classList.add('active');
    thumbnails[itemActive].classList.add('active');

    // Perbarui posisi thumbnail
    setPositionThumbnail();

    // Reset interval otomatis
    resetAutoPlay();
}

// Fungsi untuk mengatur posisi thumbnail agar terlihat
function setPositionThumbnail() {
    let activeThumbnail = thumbnails[itemActive];
    activeThumbnail.scrollIntoView({ behavior: 'smooth', inline: 'center' });
}

// Fungsi untuk navigasi tombol Next
next.onclick = function() {
    itemActive = (itemActive + 1) % countItem;
    showSlider();
}

// Fungsi untuk navigasi tombol Prev
prev.onclick = function() {
    itemActive = (itemActive - 1 + countItem) % countItem;
    showSlider();
}

// Event klik pada thumbnail untuk menampilkan item slider
thumbnails.forEach((thumbnail, index) => {
    thumbnail.onclick = function() {
        itemActive = index;
        showSlider();
    }
});

// Fungsi autoplay slider setiap 5 detik
let autoPlayInterval = setInterval(() => next.click(), 5000);

// Fungsi untuk mereset autoplay interval
function resetAutoPlay() {
    clearInterval(autoPlayInterval);
    autoPlayInterval = setInterval(() => next.click(), 5000);
}

document.addEventListener("DOMContentLoaded", function() {
    let items = document.querySelectorAll('.slider .list .item');
    let next = document.getElementById('next');
    let prev = document.getElementById('prev');
    // (Kode JavaScript lainnya)
});

