(() => {
    /**
     * Fetches the video from the server and embeds it in the page
     */
    async function fetchVideo() {
        document.body.requestFullscreen();

        // Fade out the text input and the submit button
        fadeOutByIds('textInput', 'submit');

        // Fetch the video from the server
        const response = await fetch(`/video?prompt=${encodeURIComponent(textElement.value)}`);
        const blob = await response.blob();

        const videoContainer = document.getElementById('videoContainer');
        videoContainer.innerHTML = '';  // Clear previous videos if any
        videoContainer.appendChild(createVideoElement(blob));

        // Add hotkeys to play/pause the video
        document.addEventListener('keydown', (event) => {
            if (event.key === ' ' || event.key === 'p') {
                playVideo();
            } else if (event.key === 'f') {
                document.body.requestFullscreen();
            }
        });
    }

    /**
     * Fades out the elements with the given ids
     * 
     * @param  {...string} ids
     * @returns {void}
     **/
    function fadeOutByIds(...ids) {
        ids.forEach((id) => {
            const element = document.getElementById(id);
            element.classList.add('fade-out');
            element.addEventListener('animationend', function() {
                element.style.display = 'none';
            });
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
        // Add event listener to the submit button
        document.getElementById('submit').addEventListener('click', fetchVideo);

        // Submit the form manually if we press enter key
        document.addEventListener('keydown', (event) => {
            const textElement = document.getElementById('textInput');
            const textExists = ![...textElement.classList].includes('fade-out');
            if (event.key === 'Enter' && textExists) {
                const textInput = document.getElementById('textInput');
                if (textInput.value !== '') {
                    fetchVideo();
                }
            }
        });
    });

})();