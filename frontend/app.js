/**
 * Sahayak AI - Main Application
 * ==============================
 * Handles UI interactions, API calls, and state management.
 */

// Configuration
const CONFIG = {
    // Backend API URL - Handles localhost, local IP, and file protocol
    API_BASE_URL: (function () {
        const host = window.location.hostname;
        const protocol = window.location.protocol;
        // If local file, local server, or local IP, use local backend
        if (!host || host === 'localhost' || host === '127.0.0.1' || protocol === 'file:') {
            return 'http://localhost:8000';
        }
        // REPLACE THIS URL with your actual Render backend URL after deployment
        return 'https://sahayak-ai-backend.onrender.com';
    })(),

    // Maximum recording duration in seconds
    MAX_RECORD_SECONDS: 30,

    // Enable Web Speech API fallback
    USE_WEB_SPEECH: true
};

// State
const state = {
    isRecording: false,
    isProcessing: false,
    userLocation: null,
    recorder: null,
    recordingTimer: null,
    webSpeech: null,
    voskActive: false
};

// DOM Elements
const elements = {
    chatContainer: document.getElementById('chatContainer'),
    textInput: document.getElementById('textInput'),
    sendBtn: document.getElementById('sendBtn'),
    micBtn: document.getElementById('micBtn'),
    recordingStatus: document.getElementById('recordingStatus'),
    loadingOverlay: document.getElementById('loadingOverlay'),
    statusIndicator: document.getElementById('statusIndicator'),
    locationInfo: document.getElementById('locationInfo'),
    quickActions: document.getElementById('quickActions'),
    audioPlayer: document.getElementById('audioPlayer'),
    audioVisualizer: document.getElementById('audioVisualizer')
};

// =============================================================================
// INITIALIZATION
// =============================================================================

document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 Sahayak AI initializing...');

    // Check API health
    await checkApiHealth();

    // Get user location
    getUserLocation();

    // Initialize audio systems
    state.webSpeech = useWebSpeechRecognition();
    initializeRecorder();

    // Set up event listeners
    setupEventListeners();

    console.log('✅ Sahayak AI ready');
});

/**
 * Check backend API health
 */
async function checkApiHealth() {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/health`);
        const data = await response.json();

        if (data.status === 'healthy') {
            updateStatus('Connected', false);
            console.log('✅ API healthy:', data.services);
        } else {
            updateStatus('Degraded', true);
        }
    } catch (error) {
        console.warn('⚠️ API not reachable:', error);
        updateStatus('Offline', true);

        // Show offline message
        addMessage('assistant',
            '⚠️ बैकएंड सर्वर से कनेक्ट नहीं हो पा रहा। कृपया सर्वर चलाएं या बाद में प्रयास करें।\n\n' +
            'Server command: `uvicorn main:app --reload`'
        );
    }
}

/**
 * Get user's location
 */
function getUserLocation() {
    if (!navigator.geolocation) {
        console.log('Geolocation not supported');
        updateLocationInfo('Not available');
        return;
    }

    navigator.geolocation.getCurrentPosition(
        (position) => {
            state.userLocation = {
                latitude: position.coords.latitude,
                longitude: position.coords.longitude
            };
            updateLocationInfo('Detected ✓');
            console.log('📍 Location:', state.userLocation);
        },
        (error) => {
            console.warn('Location error:', error);
            updateLocationInfo('Using default (Delhi)');
            state.userLocation = { latitude: 28.6139, longitude: 77.2090 };
        },
        { enableHighAccuracy: false, timeout: 5000 }
    );
}

/**
 * Initialize audio recorder
 */
async function initializeRecorder() {
    if (!AudioRecorder.isSupported()) {
        console.warn('Audio recording not supported');
        elements.micBtn.disabled = true;
        elements.micBtn.title = 'Voice not supported in this browser';
        return;
    }

    state.recorder = new AudioRecorder();

    state.recorder.onStart = () => {
        state.isRecording = true;
        elements.micBtn.classList.add('recording');
        elements.recordingStatus.classList.remove('hidden');
        startVisualization();
    };

    state.recorder.onStop = async (audioBlob) => {
        state.isRecording = false;
        elements.micBtn.classList.remove('recording');
        elements.recordingStatus.classList.add('hidden');
        stopVisualization();

        if (audioBlob && audioBlob.size > 0) {
            await processAudioInput(audioBlob);
        }
    };

    state.recorder.onError = (error) => {
        console.error('Recording error:', error);
        showToast('रिकॉर्डिंग में समस्या: ' + error.message);
    };
}

// =============================================================================
// EVENT LISTENERS
// =============================================================================

function setupEventListeners() {
    // Text input - Enter to send
    elements.textInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleTextSubmit();
        }
    });

    // Send button
    elements.sendBtn.addEventListener('click', handleTextSubmit);

    // Mic button
    elements.micBtn.addEventListener('click', handleMicClick);

    // Quick action buttons
    elements.quickActions.addEventListener('click', (e) => {
        if (e.target.classList.contains('quick-btn')) {
            const query = e.target.dataset.query;
            if (query) {
                elements.textInput.value = query;
                handleTextSubmit();
            }
        }
    });
}

// =============================================================================
// INPUT HANDLERS
// =============================================================================

/**
 * Handle text input submission
 */
async function handleTextSubmit() {
    const text = elements.textInput.value.trim();

    if (!text || state.isProcessing) {
        return;
    }

    // Add user message to chat
    addMessage('user', text);
    elements.textInput.value = '';

    // Send to backend
    await sendQuery({ text_query: text });
}

/**
 * Handle microphone button click
 */
async function handleMicClick() {
    if (state.isProcessing) return;

    console.log('🎤 Mic clicked. State:', { isRecording: state.isRecording, webSpeech: !!state.webSpeech });

    if (state.isRecording) {
        if (state.webSpeech && !state.voskActive) {
            console.log('Stopping Web Speech...');
            state.webSpeech.stop();
        } else {
            console.log('Stopping Local Recorder...');
            state.recorder.stop();
        }
        return;
    }

    // Attempt to start voice
    // 1. Try Web Speech API First (Better for Hindi)
    if (state.webSpeech) {
        try {
            console.log('Starting Web Speech Recognition...');
            state.webSpeech.start();
            state.voskActive = false;
            updateRecordingUI(true);
        } catch (e) {
            console.warn('Web Speech start failed, falling back to local recorder:', e);
            startLocalRecorder();
        }
    } else {
        // 2. Fallback to Local Recorder (VOSK backend)
        console.log('Web Speech not available, using Local Recorder...');
        startLocalRecorder();
    }
}

/**
 * Start local VOSK recording
 */
async function startLocalRecorder() {
    try {
        console.log('Initializing Local Recorder...');
        state.voskActive = true;
        await state.recorder.start();
        updateRecordingUI(true);

        state.recordingTimer = setTimeout(() => {
            if (state.isRecording && state.voskActive) {
                console.log('Auto-stopping local recorder (timeout)');
                state.recorder.stop();
            }
        }, CONFIG.MAX_RECORD_SECONDS * 1000);
    } catch (error) {
        console.error('Local recorder failed:', error);
        state.voskActive = false;
        showToast('Mic error: ' + error.message);
    }
}

/**
 * Update UI for recording state
 */
function updateRecordingUI(active) {
    state.isRecording = active;
    elements.micBtn.classList.toggle('recording', active);
    elements.recordingStatus.classList.toggle('hidden', !active);

    const micIcon = elements.micBtn.querySelector('.mic-icon');
    const stopIcon = elements.micBtn.querySelector('.stop-icon');

    if (active) {
        micIcon.classList.add('hidden');
        stopIcon.classList.remove('hidden');
        startVisualization();
    } else {
        micIcon.classList.remove('hidden');
        stopIcon.classList.add('hidden');
        stopVisualization();
    }
}

/**
 * Process recorded audio
 */
async function processAudioInput(audioBlob) {
    try {
        // Show processing status
        addMessage('user', '🎤 [Voice Message]');

        // Convert to base64
        const audioBase64 = await AudioRecorder.blobToBase64(audioBlob);

        // Send to backend
        await sendQuery({ audio_base64: audioBase64 });

    } catch (error) {
        console.error('Audio processing failed:', error);
        showToast('ऑडियो प्रोसेस नहीं हो पाया');
    }
}

// =============================================================================
// API COMMUNICATION
// =============================================================================

/**
 * Send query to backend API
 */
async function sendQuery(params) {
    if (state.isProcessing) {
        return;
    }

    state.isProcessing = true;
    showLoading(true);

    try {
        const requestBody = {
            ...params,
            language: 'hi'
        };

        // Add location if available
        if (state.userLocation) {
            requestBody.latitude = state.userLocation.latitude;
            requestBody.longitude = state.userLocation.longitude;
        }

        const response = await fetch(`${CONFIG.API_BASE_URL}/ask`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const data = await response.json();

        if (data.success) {
            // Show transcription if available
            if (data.transcribed_text) {
                updateLastUserMessage(data.transcribed_text);
            }

            // Add assistant response
            addMessage('assistant', data.text_response, {
                audio: data.audio_base64,
                places: data.nearby_places,
                intent: data.detected_intent
            });
        } else {
            addMessage('assistant', data.text_response || 'कुछ गड़बड़ हो गई।');
        }

    } catch (error) {
        console.error('API error:', error);
        addMessage('assistant',
            '🔌 सर्वर से कनेक्ट नहीं हो पाया। कृपया बाद में प्रयास करें।\n\n' +
            'Error: ' + error.message
        );
    } finally {
        state.isProcessing = false;
        showLoading(false);
    }
}

// =============================================================================
// UI FUNCTIONS
// =============================================================================

/**
 * Add message to chat
 */
function addMessage(role, text, extras = {}) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;

    // Avatar
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? '👤' : '🤖';

    // Content
    const content = document.createElement('div');
    content.className = 'message-content';

    const textP = document.createElement('div');
    textP.className = 'message-text';
    textP.innerHTML = formatText(text);
    content.appendChild(textP);

    // Add audio player if available
    if (extras.audio) {
        const audioDiv = document.createElement('div');
        audioDiv.className = 'message-audio';

        const playBtn = document.createElement('button');
        playBtn.className = 'play-audio-btn';
        playBtn.innerHTML = `
            <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M8 5v14l11-7z"/>
            </svg>
            <span>Play Audio</span>
        `;
        playBtn.onclick = () => playAudio(extras.audio);
        audioDiv.appendChild(playBtn);
        content.appendChild(audioDiv);

        // Auto-play
        setTimeout(() => playAudio(extras.audio), 500);
    }

    // Add nearby places if available
    if (extras.places && extras.places.length > 0) {
        const placesDiv = document.createElement('div');
        placesDiv.className = 'places-list';
        placesDiv.innerHTML = '<strong>📍 Nearby Places:</strong>';

        extras.places.slice(0, 5).forEach(place => {
            const placeItem = document.createElement('div');
            placeItem.className = 'place-item';

            placeItem.innerHTML = `
                <div class="place-info">
                    <span class="place-name">${place.name}</span>
                    <span class="place-type">${place.place_type.replace(/_/g, ' ').toUpperCase()}</span>
                </div>
                <div class="place-meta">
                    <span class="place-distance">${Math.round(place.distance_meters)}m</span>
                </div>
            `;

            // Allow clicking to open in Google Maps
            placeItem.title = 'Open in Google Maps';
            placeItem.style.cursor = 'pointer';
            placeItem.onclick = () => {
                window.open(`https://www.google.com/maps/search/?api=1&query=${place.latitude},${place.longitude}`, '_blank');
            };

            placesDiv.appendChild(placeItem);
        });

        content.appendChild(placesDiv);
    }

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);

    elements.chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * Update last user message (for transcription)
 */
function updateLastUserMessage(text) {
    const messages = elements.chatContainer.querySelectorAll('.user-message');
    if (messages.length > 0) {
        const lastMessage = messages[messages.length - 1];
        const textElement = lastMessage.querySelector('.message-text');
        if (textElement && textElement.textContent.includes('[Voice Message]')) {
            textElement.innerHTML = `🎤 "${text}"`;
        }
    }
}

/**
 * Format text with basic markdown
 */
function formatText(text) {
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>');
}

/**
 * Play audio from base64
 */
function playAudio(base64Audio) {
    try {
        const audio = elements.audioPlayer;
        audio.src = `data:audio/wav;base64,${base64Audio}`;
        audio.play().catch(e => console.warn('Audio play failed:', e));
    } catch (error) {
        console.error('Audio play error:', error);
    }
}

/**
 * Update status indicator
 */
function updateStatus(text, isError = false) {
    const indicator = elements.statusIndicator;
    indicator.querySelector('.status-text').textContent = text;
    indicator.classList.toggle('error', isError);
}

/**
 * Update location info
 */
function updateLocationInfo(text) {
    elements.locationInfo.innerHTML = `<span>📍 Location: ${text}</span>`;
}

/**
 * Show/hide loading overlay
 */
function showLoading(show) {
    elements.loadingOverlay.classList.toggle('hidden', !show);
}

/**
 * Show toast message
 */
function showToast(message) {
    // Simple alert for now, can be enhanced
    console.log('Toast:', message);
}

/**
 * Scroll chat to bottom
 */
function scrollToBottom() {
    elements.chatContainer.scrollTop = elements.chatContainer.scrollHeight;
}

// =============================================================================
// AUDIO VISUALIZATION
// =============================================================================

let visualizationInterval = null;

function startVisualization() {
    const bars = elements.audioVisualizer.querySelectorAll('.bar');

    visualizationInterval = setInterval(() => {
        if (state.recorder && state.isRecording) {
            const levels = state.recorder.getAudioLevels();
            bars.forEach((bar, i) => {
                const height = 20 + (levels[i] || 0) * 80;
                bar.style.height = `${height}%`;
            });
        }
    }, 50);
}

function stopVisualization() {
    if (visualizationInterval) {
        clearInterval(visualizationInterval);
        visualizationInterval = null;
    }
}

// =============================================================================
// WEB SPEECH API FALLBACK
// =============================================================================

/**
 * Use Web Speech API for speech-to-text (browser-based fallback)
 */
function useWebSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        console.log('Web Speech API not supported');
        return null;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'hi-IN';
    recognition.continuous = false;
    recognition.interimResults = true;

    recognition.onstart = () => {
        console.log('Voice session started');
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        elements.textInput.value = transcript;

        if (event.results[0].isFinal) {
            console.log('Final Transcript:', transcript);
            updateRecordingUI(false);
            handleTextSubmit();
        }
    };

    recognition.onerror = (event) => {
        console.error('Web Speech error:', event.error);
        updateRecordingUI(false);
        if (event.error === 'not-allowed') {
            showToast('कृपया माइक्रोफोन की अनुमति दें');
        }
    };

    recognition.onend = () => {
        updateRecordingUI(false);
    };

    return recognition;
}

// Make functions available globally for debugging
window.SahayakAI = {
    state,
    sendQuery,
    addMessage,
    CONFIG
};
