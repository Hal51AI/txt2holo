(() => {
    /**
     * Fetches the video from the server and embeds it in the page
     */
    async function fetchVideo() {
        const textElement = document.getElementById('input-prompt');
        if (textElement.value === '') {
            return;
        }

        document.body.requestFullscreen();

        // Start the fade out animation for form elements
        const inputContainer = document.getElementById('input-container');
        inputContainer.classList.add('fade-out');
        inputContainer.addEventListener('animationend', () => {
            inputContainer.style.display = 'none';
        })

        // Fetch the video from the server
        const response = await fetch(`/video?prompt=${encodeURIComponent(textElement.value)}`);
        const blob = await response.blob();

        const videoContainer = document.getElementById('video-container');
        videoContainer.innerHTML = '';  // Clear previous videos if any
        videoContainer.appendChild(createVideoElement(blob));

        // Add hotkeys to play/pause the video
        document.addEventListener('keydown', (event) => {
            if (event.key === ' ' || event.key === 'p') {
                playVideo();
            } else if (event.key === 'f') {
                if (document.fullscreenElement) {
                    document.exitFullscreen();
                } else {
                    document.body.requestFullscreen();
                }
            }
        });
    }

    /**
     * Creates a video element from a blob.
     * 
     * We create a video element with the blob as a source, then apply
     * click event handler and see the following attributes:
     * - muted
     * - autoplay
     * - loop
     * - playsinline
     * 
     * @param {Blob} blob
     * @returns {HTMLVideoElement}
     * 
     */
    function createVideoElement(blob) {
        const videoElement = document.createElement('video');
        const sourceElement = document.createElement('source');

        sourceElement.type = 'video/mp4';
        sourceElement.src = URL.createObjectURL(blob);

        videoElement.addEventListener("click", playVideo);
        videoElement.addEventListener("canplay", (event) => {
            videoElement.setAttribute('muted', '');
            videoElement.setAttribute('autoplay', '');
            videoElement.setAttribute('loop', '');
            videoElement.setAttribute('playsinline', '');
            videoElement.muted = true;
        });

        videoElement.appendChild(sourceElement);

        return videoElement;
    }

    /**
     * Plays or pauses the video
     */
    function playVideo() {
        const videoDiv = document.getElementById('video-container');
        const videoElement = videoDiv.querySelector('video');

        if (!videoElement) return;

        if (videoElement.paused) {
            videoElement.play();
        } else {
            videoElement.pause();
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        // Add event listener to the submit button
        document.getElementById('submit').addEventListener('click', fetchVideo);

        // Submit the form manually if we press enter key
        document.addEventListener('keydown', (event) => {
            const textElement = document.getElementById('input-prompt');
            const textExists = ![...textElement.classList].includes('fade-out');
            if (event.key === 'Enter' && textExists) {
                if (textElement.value !== '') {
                    fetchVideo();
                }
            }
        });
    });

})();