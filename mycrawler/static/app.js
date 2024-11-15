// Static/app.js

document.addEventListener("DOMContentLoaded", () => {
    const items = document.querySelectorAll(".slider .list .item");
    const thumbnails = document.querySelectorAll("thumbnail item");
    let index = 0;

    document.getElementById("next").addEventListener("click", () => {
        items[index].classList.remove("active");
        thumbnails[index].classList.remove("active");
        index = (index + 1) % items.length;
        items[index].classList.add("active");
        thumbnails[index].classList.add("active");
    });

    document.getElementById("prev").addEventListener("click", () => {
        items[index].classList.remove("active");
        thumbnails[index].classList.remove("active");
        index = (index - 1 + items.length) % items.length;
        items[index].classList.add("active");
        thumbnails[index].classList.add("active");
    });

    
    let countItem = items.length;
    let itemActive = 0;

    // Event Next Click
    next.onclick = function() {
        itemActive = (itemActive + 1) % countItem;
        showSlider();
    };

    // Event Prev Click
    prev.onclick = function() {
        itemActive = (itemActive - 1 + countItem) % countItem;
        showSlider();
    };

    // Auto Run Slider
    let refreshInterval = setInterval(() => {
        next.click();
    }, 5000);

    // Function to Show Slider
    function showSlider() {
        // Remove old active item
        let itemActiveOld = document.querySelector('.slider .list .item.active');
        let thumbnailActiveOld = document.querySelector('.thumbnail .item.active');
        itemActiveOld.classList.remove('active');
        thumbnailActiveOld.classList.remove('active');

        // Set new active item
        items[itemActive].classList.add('active');
        thumbnails[itemActive].classList.add('active');
        setPositionThumbnail();

        // Reset Auto Run
        clearInterval(refreshInterval);
        refreshInterval = setInterval(() => {
            next.click();
        }, 5000);
    }

    // Set Position Thumbnail
    function setPositionThumbnail() {
        let thumbnailActive = document.querySelector('.thumbnail .item.active');
        let rect = thumbnailActive.getBoundingClientRect();
        if (rect.left < 0 || rect.right > window.innerWidth) {
            thumbnailActive.scrollIntoView({ behavior: 'smooth', inline: 'center' });
        }
    }

    // Click Thumbnail
    thumbnails.forEach((thumbnail, index) => {
        thumbnail.addEventListener('click', () => {
            itemActive = index;
            showSlider();
        });
    });
});
