(() => {
    /**
     * Fetches the video from the server and embeds it in the page
     */
    async function fetchVideo() {
        const textElement = document.getElementById('textInput');
        const submitButton = document.getElementById('submit');

        textElement.style.display = 'none';
        submitButton.style.display = 'none';

        const response = await fetch(`/video?prompt=${encodeURIComponent(textElement.value)}`);
        const blob = await response.blob();

        // Create and embed the video tag
        const videoElement = document.createElement('video');
        videoElement.src = URL.createObjectURL(blob);
        videoElement.autoplay = true;
        videoElement.loop = true;
        videoElement.addEventListener("click", playVideo);

        const videoContainer = document.getElementById('videoContainer');
        videoContainer.innerHTML = '';  // Clear previous videos if any
        videoContainer.appendChild(videoElement);

        document.addEventListener('keydown', (event) => {
            if (event.key === ' ' || event.key === 'p') {
                playVideo();
            }
        });
    }

    /**
     * Plays or pauses the video
     */
    function playVideo() {
        const videoDiv = document.getElementById('videoContainer');
        const videoElement = videoDiv.querySelector('video');

        if (!videoElement) return;

        if (videoElement.paused) {
            videoElement.play();
        } else {
            videoElement.pause();
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        document.getElementById('submit').addEventListener('click', fetchVideo);

        // submit the form manually if we press enter key
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                const textInput = document.getElementById('textInput');
                if (textInput.value !== '') {
                    fetchVideo();
                }
            }
        });
    });

})();