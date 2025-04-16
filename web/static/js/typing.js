/**
 * KasongoType Typing Engine
 * Handles typing logic and session management
 */

// Audio feedback configuration
const audioFeedback = {
    enabled: true,
    sounds: {
        keypress: '/static/audio/keypress.mp3',
        error: '/static/audio/error.mp3',
        complete: '/static/audio/level_complete.mp3'
    },
    volume: 0.5
};

// Cache for audio objects
const audioCache = {};

/**
 * Play a sound effect if audio feedback is enabled
 */
function playSound(soundName) {
    if (!audioFeedback.enabled) return;
    
    // Use cached audio object or create a new one
    if (!audioCache[soundName]) {
        audioCache[soundName] = new Audio(audioFeedback.sounds[soundName]);
        audioCache[soundName].volume = audioFeedback.volume;
    }
    
    // Play the sound
    const sound = audioCache[soundName];
    
    // Reset and play (allows rapid repeated sounds)
    sound.currentTime = 0;
    sound.play().catch(error => {
        // Silently ignore errors (happens when browser requires user interaction first)
    });
}

/**
 * Toggle audio feedback on/off
 */
function toggleAudioFeedback() {
    audioFeedback.enabled = !audioFeedback.enabled;
    return audioFeedback.enabled;
}

/**
 * Calculate typing metrics
 */
function calculateMetrics(text, input, timeElapsed) {
    // Convert time to minutes
    const minutes = timeElapsed / 60;
    
    // Count errors
    let errors = 0;
    for (let i = 0; i < input.length && i < text.length; i++) {
        if (input[i] !== text[i]) {
            errors++;
        }
    }
    
    // Calculate words typed (standard: 5 characters = 1 word)
    const words = input.length / 5;
    
    // Calculate WPM
    const wpm = minutes > 0 ? words / minutes : 0;
    
    // Calculate accuracy
    const accuracy = input.length > 0 ? ((input.length - errors) / input.length) * 100 : 100;
    
    return {
        wpm: Math.round(wpm * 10) / 10,  // Round to 1 decimal place
        accuracy: Math.round(accuracy * 10) / 10,  // Round to 1 decimal place
        errors: errors,
        charactersTyped: input.length,
        timeElapsed: timeElapsed
    };
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

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        calculateMetrics,
        formatTime,
        toggleAudioFeedback,
        playSound
    };
}