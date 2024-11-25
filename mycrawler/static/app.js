// Static/app.js

document.addEventListener("DOMContentLoaded", () => {
    const items = document.querySelectorAll(".slider .list .item");
    const thumbnails = document.querySelectorAll(".thumbnail .item");
    const nextButton = document.getElementById("next");
    const prevButton = document.getElementById("prev");
    let index = 0;

    // Function to show the active slide and thumbnail
    function showSlider() {
        // Remove the active class from the current items
        document.querySelector(".slider .list .item.active").classList.remove("active");
        document.querySelector(".thumbnail .item.active").classList.remove("active");

        // Add the active class to the new items
        items[index].classList.add("active");
        thumbnails[index].classList.add("active");
        setPositionThumbnail();
    }

    // Next button event
    nextButton.addEventListener("click", () => {
        index = (index + 1) % items.length;
        showSlider();
    });

    // Prev button event
    prevButton.addEventListener("click", () => {
        index = (index - 1 + items.length) % items.length;
        showSlider();
    });

    // // Auto-run slider every 5 seconds
    // let refreshInterval = setInterval(() => {
    //     nextButton.click();
    // }, 5000);

    // // Reset auto-run on manual navigation
    // function resetAutoRun() {
    //     clearInterval(refreshInterval);
    //     refreshInterval = setInterval(() => {
    //         nextButton.click();
    //     }, 5000);
    // }

    // Set the thumbnail position
    function setPositionThumbnail() {
        const thumbnailActive = document.querySelector(".thumbnail .item.active");
        const rect = thumbnailActive.getBoundingClientRect();
        if (rect.left < 0 || rect.right > window.innerWidth) {
            thumbnailActive.scrollIntoView({ behavior: "smooth", inline: "center" });
        }
    }

    // Click event for each thumbnail
    thumbnails.forEach((thumbnail, thumbIndex) => {
        thumbnail.addEventListener("click", () => {
            index = thumbIndex;
            showSlider();
            resetAutoRun();
        });
    });
});

// Add scroll effect to header
window.addEventListener('scroll', function() {
    const header = document.querySelector('header');
    if (window.scrollY > 50) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
});
