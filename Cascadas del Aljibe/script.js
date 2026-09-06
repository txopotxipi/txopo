let currentImageIndex = 0;
let sliderInterval;
let autoSlideActive = false;

function openSlider(index) {
    currentImageIndex = index;
    updateSlider();
    document.getElementById('sliderModal').classList.remove('hidden');
    document.getElementById('sliderImages').style.transition = 'transform 0.5s ease-in-out';
}

function closeSlider() {
    document.getElementById('sliderModal').classList.add('hidden');
}

function updateSlider() {
    const images = document.querySelectorAll('#sliderImages img');
    images.forEach((img, i) => {
        img.classList.remove('active');
        img.style.transform = 'translateX(' + (i - currentImageIndex) * 100 + '%)';
    });
    document.querySelectorAll('#sliderImages img')[currentImageIndex].classList.add('active');
}

function nextImage() {
    currentImageIndex = (currentImageIndex + 1) % 22;
    updateSlider();
}

function prevImage() {
    currentImageIndex = (currentImageIndex - 1 + 22) % 22;
    updateSlider();
}

function toggleAutoSlide() {
    if (autoSlideActive) {
        clearInterval(sliderInterval);
        autoSlideActive = false;
        document.getElementById('autoSlideText').textContent = 'Play';
    } else {
        sliderInterval = setInterval(nextImage, 3000);
        autoSlideActive = true;
        document.getElementById('autoSlideText').textContent = 'Pause';
    }
}

// Close slider when clicking outside the modal content
document.getElementById('sliderModal').addEventListener('click', function(event) {
    if (event.target.id === 'sliderModal') {
        closeSlider();
    }
});