(() => {
    /**
     * Fetches the video from the server and embeds it in the page
     */
    async function fetchVideo() {
        const loaderClassName = 'lds-ripple';

        const textElement = document.getElementById('input-prompt');
        if (textElement.value === '') {
            return;
        }

        // Fullscreen crashes on iOS
        if (!isIOS()) {
            document.body.requestFullscreen();
        }

        // Start loader animation
        displayLoader(loaderClassName, 'inline-block');

        // Start the fade out animation for form elements
        const inputContainer = document.getElementById('input-container');
        inputContainer.classList.add('fade-out');
        inputContainer.addEventListener('animationend', () => {
            inputContainer.style.display = 'none';
        })

        // Fetch the video from the server
        const response = await fetch(`/video?prompt=${encodeURIComponent(textElement.value)}`);
        const blob = await response.blob();

        // End loader animation
        displayLoader(loaderClassName, 'none');

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
            } else if (event.key === 'r') {
                window.location.reload();
            }
        });
    }

    /**
     * Checks if the user is using an iOS device
     * 
     * @returns {boolean}
     */
    function isIOS() {
        return /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    }

    /**
     * Set the display style of the loader element
     *  
     * @param {string} className    The class name of the loader element
     * @param {string} displayStyle The display style of the loader element
     * @returns {void}
     * 
     */
    function displayLoader(className, displayStyle) {
        const [loader] = document.getElementsByClassName(className);
        loader.style.display = displayStyle
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

        videoElement.classList.add('video-element');
        videoElement.setAttribute('autoplay', '');
        videoElement.setAttribute('loop', '');
        videoElement.setAttribute('playsinline', '');
        videoElement.setAttribute('muted', '');
        videoElement.setAttribute('preload', 'metadata');
        videoElement.muted = true;

        sourceElement.type = 'video/mp4';
        sourceElement.src = URL.createObjectURL(blob);

        videoElement.addEventListener("click", playVideo);
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

    /**
     * Inverts the input prompt
     * 
     * @param {boolean} invert
     * @returns {void}
     * 
     */
    function flipTextInput(invert) {
        const inputPrompt = document.getElementById('input-prompt');
        inputPrompt.style.transform = invert ? 'scaleX(-1)' : '';
        inputPrompt.style.paddingLeft = invert ? '80px' : '';
        window.localStorage.setItem('flipTextInput', invert);
    }

    /**
     * Creates the navigation overlays
     * 
     * @returns {void}
     * 
     */
    function createOverlays() {
        const overlays = [
            {
                className: 'top-overlay',
                clickHandler: () => window.location.reload(),
            },
            {
                className: 'left-overlay',
                clickHandler: () => flipTextInput(true),
            },
            {
                className: 'right-overlay',
                clickHandler: () => flipTextInput(false),
            }
        ]

        overlays.forEach((overlay) => {
            const overlayElement = document.querySelector(`.${overlay.className}`);

            overlayElement.addEventListener("click", overlay.clickHandler);
            overlayElement.addEventListener('mouseover', () => {
                overlayElement.style.backgroundColor = 'rgba(192, 192, 192, 0.1)'
            });
            overlayElement.addEventListener('mouseout', () => {
                overlayElement.style.backgroundColor = 'rgba(0, 0, 0, 0)'
            });
        })
    }

    document.addEventListener('DOMContentLoaded', () => {
        // Flip the input text from previous session
        flipTextInput(localStorage.flipTextInput == 'true');

        // Add event listener to the submit button
        document.getElementById('submit').addEventListener('click', fetchVideo);

        // Add navigation overlays
        createOverlays();

        // Submit the form manually if we press enter key
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                const textElement = document.getElementById('input-prompt');
                const textExists = ![...textElement.classList].includes('fade-out');
                if (textExists && textElement.value !== '') {
                    fetchVideo();
                }
            } else if (event.ctrlKey && event.key === 'ArrowLeft') {
                flipTextInput(true);
            } else if (event.ctrlKey && event.key === 'ArrowRight') {
                flipTextInput(false);
            }
        });
    });

})();