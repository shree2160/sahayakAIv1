/**
 * Sahayak AI - Audio Recorder Module
 * ===================================
 * Handles voice recording using the MediaRecorder API.
 * Supports WebM/Opus format for efficient audio capture.
 */

class AudioRecorder {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.stream = null;
        this.isRecording = false;

        // Audio context for visualization
        this.audioContext = null;
        this.analyser = null;
        this.dataArray = null;

        // Callbacks
        this.onStart = null;
        this.onStop = null;
        this.onData = null;
        this.onError = null;
    }

    /**
     * Check if browser supports audio recording
     */
    static isSupported() {
        return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
    }

    /**
     * Request microphone permission and initialize recording
     */
    async initialize() {
        if (!AudioRecorder.isSupported()) {
            throw new Error('Audio recording is not supported in this browser');
        }

        try {
            // Request microphone access
            this.stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    sampleRate: 16000  // VOSK prefers 16kHz
                }
            });

            // Set up audio context for visualization
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const source = this.audioContext.createMediaStreamSource(this.stream);
            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = 256;
            source.connect(this.analyser);
            this.dataArray = new Uint8Array(this.analyser.frequencyBinCount);

            console.log('🎤 Microphone initialized successfully');
            return true;

        } catch (error) {
            console.error('Microphone initialization failed:', error);

            if (error.name === 'NotAllowedError') {
                throw new Error('माइक्रोफोन की अनुमति नहीं दी गई। कृपया अनुमति दें।');
            } else if (error.name === 'NotFoundError') {
                throw new Error('कोई माइक्रोफोन नहीं मिला। कृपया माइक्रोफोन कनेक्ट करें।');
            } else {
                throw new Error('माइक्रोफोन शुरू करने में समस्या: ' + error.message);
            }
        }
    }

    /**
     * Start recording audio
     */
    async start() {
        if (this.isRecording) {
            console.warn('Already recording');
            return;
        }

        // Initialize if not already done
        if (!this.stream) {
            await this.initialize();
        }

        // Reset chunks
        this.audioChunks = [];

        // Determine best audio format
        const mimeType = this._getBestMimeType();
        console.log('Using MIME type:', mimeType);

        try {
            this.mediaRecorder = new MediaRecorder(this.stream, {
                mimeType: mimeType,
                audioBitsPerSecond: 128000
            });
        } catch (e) {
            // Fallback without options
            this.mediaRecorder = new MediaRecorder(this.stream);
        }

        // Handle data available event
        this.mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                this.audioChunks.push(event.data);
                if (this.onData) {
                    this.onData(event.data);
                }
            }
        };

        // Handle recording stop
        this.mediaRecorder.onstop = () => {
            this.isRecording = false;
            const audioBlob = new Blob(this.audioChunks, { type: mimeType });

            if (this.onStop) {
                this.onStop(audioBlob);
            }
        };

        // Handle errors
        this.mediaRecorder.onerror = (event) => {
            console.error('MediaRecorder error:', event.error);
            this.isRecording = false;
            if (this.onError) {
                this.onError(event.error);
            }
        };

        // Start recording
        this.mediaRecorder.start(100);  // Collect data every 100ms
        this.isRecording = true;

        if (this.onStart) {
            this.onStart();
        }

        console.log('🔴 Recording started');
    }

    /**
     * Stop recording and return audio blob
     */
    stop() {
        if (!this.isRecording || !this.mediaRecorder) {
            console.warn('Not recording');
            return null;
        }

        this.mediaRecorder.stop();
        console.log('⏹️ Recording stopped');
    }

    /**
     * Get audio levels for visualization
     */
    getAudioLevels() {
        if (!this.analyser || !this.dataArray) {
            return new Array(5).fill(0);
        }

        this.analyser.getByteFrequencyData(this.dataArray);

        // Get 5 frequency bands for visualization
        const bands = 5;
        const bandSize = Math.floor(this.dataArray.length / bands);
        const levels = [];

        for (let i = 0; i < bands; i++) {
            let sum = 0;
            for (let j = 0; j < bandSize; j++) {
                sum += this.dataArray[i * bandSize + j];
            }
            levels.push(sum / bandSize / 255);  // Normalize to 0-1
        }

        return levels;
    }

    /**
     * Convert audio blob to base64
     */
    static async blobToBase64(blob) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onloadend = () => {
                // Remove data URL prefix
                const base64 = reader.result.split(',')[1];
                resolve(base64);
            };
            reader.onerror = reject;
            reader.readAsDataURL(blob);
        });
    }

    /**
     * Get best supported MIME type
     */
    _getBestMimeType() {
        const types = [
            'audio/webm;codecs=opus',
            'audio/webm',
            'audio/ogg;codecs=opus',
            'audio/mp4',
            'audio/wav'
        ];

        for (const type of types) {
            if (MediaRecorder.isTypeSupported(type)) {
                return type;
            }
        }

        return '';  // Let browser decide
    }

    /**
     * Clean up resources
     */
    destroy() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }

        if (this.audioContext) {
            this.audioContext.close();
            this.audioContext = null;
        }

        this.mediaRecorder = null;
        this.isRecording = false;
        console.log('🎤 Recorder destroyed');
    }
}

// Export for use in app.js
window.AudioRecorder = AudioRecorder;
