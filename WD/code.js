let currentMode = 'queue';
let detectionActive = false;
let currentPlayingSong = '';

// DOM elements
const statusElement = document.getElementById('status');
const emotionElement = document.getElementById('emotion');
const songElement = document.getElementById('song');
const playerElement = document.getElementById('player');

function initPlayer() {
    document.getElementById('mode-queue').addEventListener('click', () => setMode('queue'));
    document.getElementById('mode-emotion').addEventListener('click', () => setMode('emotion'));
    document.getElementById('mode-random').addEventListener('click', () => setMode('random'));

    document.getElementById('start-btn').addEventListener('click', startDetection);
    document.getElementById('stop-btn').addEventListener('click', stopDetection);

    updateStatus('Ready');
}

function setMode(mode) {
    currentMode = mode;
    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.mode === mode);
    });

    if (mode === 'emotion' && !detectionActive) {
        startDetection();
    }
}

function updateStatus(message) {
    statusElement.textContent = message;
}

function updateEmotion(emotion) {
    emotionElement.textContent = emotion.charAt(0).toUpperCase() + emotion.slice(1);
    emotionElement.className = `emotion-${emotion}`;
}

function updateSongInfo(song) {
    songElement.textContent = song;
}

// Start and Stop detection
async function startDetection() {
    if (detectionActive) return;

    updateStatus('Starting detection...');
    const result = await eel.start_emotion_detection()();
    if (result.status === 'success') {
        detectionActive = true;
        document.getElementById('start-btn').disabled = true;
        document.getElementById('stop-btn').disabled = false;
    } else {
        showAlert(result.message || 'Failed to start detection');
    }
}

async function stopDetection() {
    if (!detectionActive) return;

    updateStatus('Stopping...');
    const result = await eel.stop_detection()();
    if (result.status === 'success') {
        detectionActive = false;
        document.getElementById('start-btn').disabled = false;
        document.getElementById('stop-btn').disabled = true;
        updateStatus('Ready');
    }
}

// Main function exposed to Python
eel.expose(update_player);
function update_player(emotion, song) {
    updateEmotion(emotion);
    updateSongInfo(song);
    updateStatus(`Playing ${emotion} music`);

    const audioPlayer = document.getElementById('player');

    const newSrc = `songs/${song}`;
    const currentSrc = decodeURIComponent(audioPlayer.src);

    // If it's the same song and already playing or paused, don't reload
    if (currentPlayingSong === song && !audioPlayer.ended && !audioPlayer.paused) {
        console.log('Same song already playing. Skipping reload.');
        return;
    }

    currentPlayingSong = song;

    audioPlayer.pause();
    audioPlayer.currentTime = 0;
    audioPlayer.src = newSrc;
    audioPlayer.load();
    audioPlayer.play();
}

eel.expose(update_status);
function update_status(message) {
    statusElement.textContent = message;
}

eel.expose(show_alert);
function show_alert(message) {
    alert(message);
}

playerElement.addEventListener('error', (e) => {
    console.error('Audio error:', e);
});

document.addEventListener('DOMContentLoaded', initPlayer);
