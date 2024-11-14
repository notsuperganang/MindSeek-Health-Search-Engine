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

    
});
