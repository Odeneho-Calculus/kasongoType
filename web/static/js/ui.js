/**
 * KasongoType UI Module
 * Handles user interface interactions and animations
 */

document.addEventListener('DOMContentLoaded', function () {
    // Initialize cyberpunk UI effects
    initCyberpunkEffects();

    // Setup navigation highlighting
    highlightCurrentNavItem();

    // Setup typing interface if on the typing page
    if (document.getElementById('text-display')) {
        initTypingInterface();
    }
});

/**
 * Initialize cyberpunk visual effects
 */
function initCyberpunkEffects() {
    // Add glitch effect to headings
    document.querySelectorAll('h1, h2, h3').forEach(heading => {
        heading.classList.add('glitch-text');

        // Create glitch animation at random intervals
        setInterval(() => {
            heading.classList.add('glitch-active');
            setTimeout(() => {
                heading.classList.remove('glitch-active');
            }, 200);
        }, Math.random() * 10000 + 5000);
    });

    // Add scanner effect to neon borders
    document.querySelectorAll('.neon-border').forEach(element => {
        const scanner = document.createElement('div');
        scanner.className = 'neon-scanner';
        element.appendChild(scanner);
    });
}

/**
 * Highlight current navigation item based on URL
 */
function highlightCurrentNavItem() {
    const currentPath = window.location.pathname;
    document.querySelectorAll('nav a').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

/**
 * Initialize the typing interface
 */
/**
 * Initialize the typing interface
 */
function initTypingInterface() {
    const textDisplay = document.getElementById('text-display');
    const hiddenInput = document.getElementById('hidden-input');
    const exerciseTitle = document.getElementById('exercise-title');
    const resetButton = document.getElementById('reset-btn');
    const newExerciseButton = document.getElementById('new-exercise-btn');
    const levelSelect = document.getElementById('level-select');
    const resultsPanel = document.getElementById('results-panel');
    const tryAgainButton = document.getElementById('try-again-btn');
    const nextExerciseButton = document.getElementById('next-exercise-btn');

    // Stats elements
    const wpmDisplay = document.getElementById('wpm');
    const accuracyDisplay = document.getElementById('accuracy');
    const timeDisplay = document.getElementById('time');

    // Results elements
    const finalWpm = document.getElementById('final-wpm');
    const finalAccuracy = document.getElementById('final-accuracy');
    const finalTime = document.getElementById('final-time');
    const finalErrors = document.getElementById('final-errors');

    // Typing session variables
    let currentSessionId = null;
    let currentExercise = null;
    let typingStarted = false;
    let typingInterval = null;
    let sessionStartTime = null;

    // Check URL parameters for exercise selection
    const urlParams = new URLSearchParams(window.location.search);
    const exerciseIdParam = urlParams.get('exercise');
    const levelParam = urlParams.get('level');

    //new mods
    let countdownTimer = null;
    let timeLimit = 60; // Default 60 seconds time limit
    const timerModeSelect = document.getElementById('timer-mode'); // Add this select element to your HTML

    if (exerciseIdParam && levelParam) {
        // Load specific exercise
        loadExercise(levelParam, exerciseIdParam);
        // Set level select to match
        levelSelect.value = levelParam;
    } else {
        // Load random exercise
        startNewSession();
    }

    // Event listeners
    hiddenInput.addEventListener('input', function (event) {
        handleTyping(event);

        // Force stats update after each keystroke for real-time feedback
        if (typingStarted) {
            updateStats();
        }
    });
    resetButton.addEventListener('click', resetExercise);
    newExerciseButton.addEventListener('click', startNewSession);
    tryAgainButton.addEventListener('click', resetExercise);
    nextExerciseButton.addEventListener('click', startNewSession);

    // Focus hidden input when clicking anywhere in the typing area
    textDisplay.addEventListener('click', () => {
        hiddenInput.focus();
    });


    function startTimer() {
        if (timerModeSelect.value === 'countdown') {
            // Countdown mode
            let timeRemaining = timeLimit;
            timeDisplay.textContent = formatTime(timeRemaining);

            countdownTimer = setInterval(() => {
                timeRemaining--;
                timeDisplay.textContent = formatTime(timeRemaining);

                if (timeRemaining <= 0) {
                    clearInterval(countdownTimer);
                    // Force completion when time is up
                    handleSessionComplete({
                        wpm: parseFloat(wpmDisplay.textContent),
                        accuracy: parseFloat(accuracyDisplay.textContent),
                        time_elapsed: timeLimit,
                        errors: document.querySelectorAll('.char.error').length
                    });
                }
            }, 1000);
        } else {
            // Count-up mode (existing functionality)
            typingInterval = setInterval(updateStats, 1000);
        }
    }

    /**
     * Load a specific exercise by level and ID
     */
    function loadExercise(level, exerciseId) {
        fetch(`/api/exercise/${level}/${exerciseId}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    const exercise = data.exercise;

                    // Start new session with this exercise
                    fetch('/api/session/start', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            exercise_id: exercise.id,
                            level: level
                        })
                    })
                        .then(response => response.json())
                        .then(sessionData => {
                            if (sessionData.status === 'success') {
                                // Set current session
                                currentSessionId = sessionData.session_id;
                                currentExercise = sessionData.exercise;

                                // Display exercise
                                displayExercise(currentExercise);

                                // Reset UI state
                                resetUIState();

                                // Play ready sound
                                playSound('keypress');
                            }
                        });
                }
            });
    }

    /**
     * Start a new typing session with a random exercise
     */
    function startNewSession() {
        // Hide results panel if visible
        resultsPanel.classList.add('hidden');

        // Get selected level
        const level = levelSelect.value;

        // Reset UI state before starting the countdown
        resetUIState();

        // Show pre-countdown
        displayCountdown(3, () => {
            // Only start after 3-2-1
            fetch('/api/session/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    level: level
                })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        // Set current session
                        currentSessionId = data.session_id;
                        currentExercise = data.exercise;

                        // Display exercise
                        displayExercise(currentExercise);

                        // Focus on input
                        hiddenInput.focus();

                        // Play ready sound
                        playSound('keypress');
                    }
                });
        });
    }

    /**
     * Add visual countdown
     */
    function displayCountdown(seconds, callback) {
        let count = seconds;
        const countdownEl = document.createElement('div');
        countdownEl.id = 'pre-countdown';
        countdownEl.className = 'countdown-overlay';
        countdownEl.textContent = count;

        // Style the countdown element
        countdownEl.style.position = 'fixed';
        countdownEl.style.top = '50%';
        countdownEl.style.left = '50%';
        countdownEl.style.transform = 'translate(-50%, -50%)';
        countdownEl.style.fontSize = '4rem';
        countdownEl.style.fontWeight = 'bold';
        countdownEl.style.color = '#00ff41';
        countdownEl.style.zIndex = '1000';
        countdownEl.style.textShadow = '0 0 10px #00ff41';

        document.body.appendChild(countdownEl);

        const interval = setInterval(() => {
            count--;
            countdownEl.textContent = count;

            // Play countdown sound
            playSound('keypress');

            if (count <= 0) {
                clearInterval(interval);
                countdownEl.remove();
                callback();
            }
        }, 1000);
    }

    /**
     * Display the exercise text in the UI
     */
    function displayExercise(exercise) {
        // Set exercise title
        exerciseTitle.textContent = exercise.title;

        // Create character spans for the text
        const textWrapper = document.createElement('div');
        textWrapper.className = 'text-wrapper';

        exercise.text.split('').forEach(char => {
            const charSpan = document.createElement('span');
            charSpan.className = 'char';
            charSpan.textContent = char;
            textWrapper.appendChild(charSpan);
        });

        // Replace text display content
        textDisplay.innerHTML = '';
        textDisplay.appendChild(textWrapper);
    }

    /**
     * Reset UI state for a new typing session
     */
    function resetUIState() {
        // Clear input
        hiddenInput.value = '';
        hiddenInput.disabled = false;

        // Reset flags
        typingStarted = false;
        sessionStartTime = null;

        // Clear all intervals
        if (typingInterval) {
            clearInterval(typingInterval);
            typingInterval = null;
        }

        if (countdownTimer) {
            clearInterval(countdownTimer);
            countdownTimer = null;
        }

        // Reset stats
        wpmDisplay.textContent = '0';
        accuracyDisplay.textContent = '100%';

        // Set timer display based on mode
        if (timerModeSelect.value === 'countdown') {
            const timeLimit = parseInt(document.getElementById('time-limit').value) || 60;
            timeDisplay.textContent = formatTime(timeLimit);
        } else {
            timeDisplay.textContent = '0s';
        }

        // Reset character styling
        document.querySelectorAll('.char').forEach(span => {
            span.className = 'char';
        });

        // Hide results panel
        resultsPanel.classList.add('hidden');

        // Focus input
        hiddenInput.focus();
    }

    /**
     * Handle typing input
     */
    function handleTyping(event) {
        const input = event.target.value;

        // Check if the exercise is complete locally before sending to server
        if (currentExercise && input.length >= currentExercise.text.length) {
            // Show completion immediately if user has typed enough characters
            handleSessionComplete({
                wpm: parseFloat(wpmDisplay.textContent),
                accuracy: parseFloat(accuracyDisplay.textContent),
                time_elapsed: (Date.now() - sessionStartTime) / 1000,
                errors: document.querySelectorAll('.char.error').length
            });
            return;
        }

        // If no session or no input, return
        if (!currentSessionId || input.length === 0) {
            return;
        }



        // Start timer on first keystroke
        if (!typingStarted && input.length > 0) {
            typingStarted = true;
            sessionStartTime = Date.now();

            // Start the appropriate timer
            startTimer();

            // Play keystroke sound
            playSound('keypress');
        }

        // Send keystroke to server
        const lastChar = input.charAt(input.length - 1);

        fetch(`/api/session/${currentSessionId}/keystroke`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                key: lastChar,
                exercise_id: currentExercise.id
            })
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Server responded with status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.status === 'success') {
                    // Update character styling
                    updateCharacterStyling(input);

                    // Update stats display from server data
                    if (data.metrics) {
                        wpmDisplay.textContent = data.metrics.wpm.toFixed(1);
                        accuracyDisplay.textContent = data.metrics.accuracy.toFixed(1) + '%';

                        // Update time display
                        const timeElapsed = data.metrics.time_elapsed;
                        timeDisplay.textContent = formatTime(timeElapsed);
                    }

                    // Play sound based on correctness
                    if (data.result) {
                        if (data.result.correct) {
                            playSound('keypress');
                        } else {
                            playSound('error');
                        }
                    }

                    // Check if session is complete
                    if (data.result && data.result.complete) {
                        handleSessionComplete(data.metrics);
                    }
                } else {
                    console.warn('Server returned non-success status:', data.message);
                }
            })
            .catch(error => {
                console.error('Error sending keystroke:', error);

                // Implement fallback for error cases - continue locally
                updateCharacterStyling(input);
                updateStats(); // Update stats locally

                // Check if we're at the end of the text and complete locally if necessary
                if (input.length >= currentExercise.text.length) {
                    handleSessionComplete({
                        wpm: parseFloat(wpmDisplay.textContent),
                        accuracy: parseFloat(accuracyDisplay.textContent),
                        time_elapsed: (Date.now() - sessionStartTime) / 1000,
                        errors: document.querySelectorAll('.char.error').length
                    });
                }
            });
    }

    /**
     * Update character styling based on user input
     */
    function updateCharacterStyling(input) {
        const chars = document.querySelectorAll('.char');

        for (let i = 0; i < chars.length; i++) {
            if (i < input.length) {
                // Character has been typed
                if (input.charAt(i) === chars[i].textContent) {
                    chars[i].className = 'char correct';
                } else {
                    chars[i].className = 'char error';
                }
            } else if (i === input.length) {
                // Current character
                chars[i].className = 'char current';
            } else {
                // Not typed yet
                chars[i].className = 'char';
            }
        }
    }

    /**
     * Update typing statistics
     */
    function updateStats() {
        if (!typingStarted || !sessionStartTime) return;

        const elapsedTime = (Date.now() - sessionStartTime) / 1000;
        // Update time display
        timeDisplay.textContent = formatTime(elapsedTime);

        // Calculate and update WPM and accuracy locally
        const input = hiddenInput.value;
        const text = currentExercise.text;

        // Count errors properly
        let errors = 0;
        for (let i = 0; i < input.length && i < text.length; i++) {
            if (input[i] !== text[i]) errors++;
        }

        // Standard WPM calculation: (characters typed / 5) / minutes
        const typedChars = input.length;
        const minutes = Math.max(elapsedTime / 60, 0.01); // Prevent division by zero
        const wpm = (typedChars / 5) / minutes;

        // Accuracy calculation
        const accuracy = input.length > 0 ? ((input.length - errors) / input.length) * 100 : 100;

        // Update display with clearer formatting
        wpmDisplay.textContent = wpm.toFixed(1);
        accuracyDisplay.textContent = accuracy.toFixed(1) + '%';

        // Log for debugging
        console.log(`Stats update - WPM: ${wpm.toFixed(1)}, Accuracy: ${accuracy.toFixed(1)}%, Chars: ${typedChars}, Errors: ${errors}, Time: ${elapsedTime.toFixed(1)}s`);
    }

    /**
     * Handle session completion
     */
    function handleSessionComplete(metrics) {
        // Stop all timers
        if (typingInterval) {
            clearInterval(typingInterval);
            typingInterval = null;
        }

        if (countdownTimer) {
            clearInterval(countdownTimer);
            countdownTimer = null;
        }

        // Calculate final metrics manually to ensure accuracy
        const input = hiddenInput.value;
        const text = currentExercise.text;
        const elapsedTime = (Date.now() - sessionStartTime) / 1000;

        // Count errors
        let errors = 0;
        for (let i = 0; i < input.length && i < text.length; i++) {
            if (input[i] !== text[i]) errors++;
        }

        // Calculate WPM: (characters typed / 5) / minutes
        const typedChars = input.length;
        const minutes = Math.max(elapsedTime / 60, 0.01);
        const wpm = (typedChars / 5) / minutes;

        // Calculate accuracy
        const accuracy = input.length > 0 ? ((input.length - errors) / input.length) * 100 : 100;

        // Use our calculated metrics instead of potentially incorrect server metrics
        const finalMetrics = {
            wpm: wpm,
            accuracy: accuracy,
            time_elapsed: elapsedTime,
            errors: errors
        };

        // Update final results display
        finalWpm.textContent = finalMetrics.wpm.toFixed(1);
        finalAccuracy.textContent = finalMetrics.accuracy.toFixed(1) + '%';
        finalTime.textContent = formatTime(finalMetrics.time_elapsed);
        finalErrors.textContent = finalMetrics.errors;

        // Show results panel
        resultsPanel.classList.remove('hidden');
        resultsPanel.style.display = 'block';

        // Play completion sound
        playSound('complete');

        // Disable input to prevent further typing
        hiddenInput.disabled = true;

        // Log the final metrics for debugging
        console.log("Session complete - Final metrics:", finalMetrics);

        // Save to server if needed
        saveSessionResults(finalMetrics);
    }

    // Add this helper function to save results to the server
    function saveSessionResults(metrics) {
        // Only save if we have a valid session ID
        if (!currentSessionId || !currentExercise) return;

        fetch(`/api/session/${currentSessionId}/complete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                exercise_id: currentExercise.id,
                metrics: metrics
            })
        })
            .then(response => response.json())
            .then(data => {
                console.log("Session results saved:", data);
            })
            .catch(error => {
                console.error("Error saving session results:", error);
            });
    }

    /**
     * Reset the current exercise
     */
    function resetExercise() {
        // Hide results panel if visible
        resultsPanel.classList.add('hidden');

        // If we have the current exercise, reload it
        if (currentExercise) {
            // Start new session with same exercise
            fetch('/api/session/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    exercise_id: currentExercise.id,
                    level: levelSelect.value
                })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        // Set current session
                        currentSessionId = data.session_id;

                        // Reset UI state
                        resetUIState();
                    }
                });
        } else {
            // Fallback to new random exercise
            startNewSession();
        }
    }

    /**
     * Format time in seconds to a readable string
     */
    function formatTime(seconds) {
        if (seconds < 60) {
            return `${seconds.toFixed(1)}s`;
        } else {
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = seconds % 60;
            return `${minutes}m ${remainingSeconds.toFixed(0)}s`;
        }
    }

    /**
     * Play sound effect
     */
    function playSound(soundName) {
        if (typeof audioFeedback !== 'undefined' && !audioFeedback.enabled) {
            return; // Audio feedback is disabled
        }

        // Define sounds if not defined in global scope
        const sounds = {
            keypress: '/static/audio/keypress.mp3',
            error: '/static/audio/error.mp3',
            complete: '/static/audio/level_complete.mp3'
        };

        const sound = new Audio(sounds[soundName]);
        sound.volume = 0.5; // Lower volume

        sound.play().catch(() => {
            // Silently fail if sound can't be played
            // This happens in browsers that require user interaction first
        });
    }
}