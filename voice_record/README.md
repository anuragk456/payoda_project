# Voice Recorder with Intelligent Noise Filtering

An advanced web-based voice recorder that automatically segments recordings based on silence detection with sophisticated noise filtering capabilities. Perfect for interviews, meetings, and voice notes.

## Features

- **Automatic Recording Segmentation**: Creates new recording segments after 4 seconds of detected silence
- **Advanced Noise Filtering**: Intelligently distinguishes between human voice and background noise
- **Real-time Voice Detection**: Uses frequency analysis to filter out ambient sounds
- **Loop Recording Mode**: Continuous recording with automatic segment creation
- **Multiple Audio Downloads**: Download individual segments or all recordings at once
- **Visual Feedback**: Real-time status updates and silence timer display

## How It Works

### Voice Detection and Noise Filtering

The application uses sophisticated audio analysis to distinguish between human speech and background noise:

#### 1. Audio Analysis Setup (`setupAudioAnalysis()`)
```javascript
setupAudioAnalysis() {
    this.audioContext = new AudioContext();
    this.analyser = this.audioContext.createAnalyser();
    this.analyser.fftSize = 512;  // Frequency resolution
    this.analyser.smoothingTimeConstant = 0.3;  // Temporal smoothing
}
```

#### 2. Human Voice Frequency Analysis (`getVolumeLevel()`)
The core noise filtering logic focuses on human voice frequency range:

- **Voice Frequency Range**: 85Hz - 3400Hz (typical human speech)
- **Frequency Bin Analysis**: Each bin represents ~86Hz (44100Hz sample rate / 512 FFT size)
- **Noise Separation**: Audio outside voice range is considered background noise

```javascript
getVolumeLevel() {
    // Focus on human voice frequency range (85Hz - 3400Hz)
    const voiceStartBin = Math.floor(85 / 86);   // ~1
    const voiceEndBin = Math.floor(3400 / 86);   // ~40

    let voiceSum = 0;
    let noiseSum = 0;

    for (let i = 0; i < bufferLength; i++) {
        if (i >= voiceStartBin && i <= voiceEndBin) {
            voiceSum += dataArray[i];  // Voice frequencies
        } else {
            noiseSum += dataArray[i];  // Noise frequencies
        }
    }

    // Return voice level minus noise for better discrimination
    return Math.max(0, voiceAverage - (noiseAverage * 0.5));
}
```

#### 3. Voice Detection Logic (`isVoiceDetected()`)
Two-tier filtering system:

```javascript
isVoiceDetected(volume) {
    // Voice must pass both thresholds
    return volume > this.NOISE_GATE_THRESHOLD && volume > this.VOICE_THRESHOLD;
}
```

**Threshold Configuration:**
- `NOISE_GATE_THRESHOLD = 40`: Blocks low-level ambient sounds
- `VOICE_THRESHOLD = 80`: Minimum level for actual human voice
- `SILENCE_THRESHOLD = 50`: Higher threshold to ignore background noise

#### 4. Silence Detection (`startSilenceDetection()`)
Continuous monitoring at 100ms intervals:

```javascript
startSilenceDetection() {
    this.volumeCheckInterval = setInterval(() => {
        const volume = this.getVolumeLevel();
        const isVoice = this.isVoiceDetected(volume);

        if (!isVoice) {
            // Start 4-second countdown for new segment
            this.startSilenceTimer();
        } else {
            // Voice detected, reset timer
            this.resetSilenceTimer();
        }
    }, 100);
}
```

### Recording Segmentation Logic

#### Automatic Segment Creation
When 4 seconds of silence (no voice) is detected:

1. **Current segment stops** (`createNewRecordingSegment()`)
2. **Audio blob created** from accumulated chunks
3. **New segment starts** automatically if still recording
4. **Silence detection restarts** for the new segment

#### Segment Management
```javascript
createAudioBlob() {
    const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
    this.audioBlobs.push(audioBlob);
    this.recordingCount++;

    if (this.isRecording) {
        this.startNewSegment();  // Continue recording
    }
}
```

## Audio Processing Pipeline

1. **Microphone Input** → Enhanced audio constraints
2. **Web Audio API** → Real-time frequency analysis
3. **Frequency Filtering** → Voice vs. noise separation
4. **Threshold Checking** → Multi-level voice detection
5. **Silence Timing** → 4-second countdown
6. **Automatic Segmentation** → New recording creation

## Browser Audio Enhancements

The recorder uses optimized audio constraints for interview quality:

```javascript
audio: {
    echoCancellation: true,    // Remove echo
    noiseSuppression: true,    // Browser-level noise reduction
    autoGainControl: true,     // Automatic volume adjustment
    sampleRate: 44100,         // High-quality sampling
    channelCount: 1,           // Mono for voice focus
    latency: 0.01,             // Low latency processing
    volume: 1.0                // Full volume capture
}
```

## Project Structure

```
voice_record/
├── voice-recorder/
│   ├── src/
│   │   ├── app/
│   │   │   └── app.component.ts     # Angular voice recorder component
│   │   ├── main.ts                  # Angular bootstrap
│   │   └── styles.css               # Styling
│   ├── index.html                   # Standalone HTML version
│   ├── package.json                 # Dependencies
│   └── angular.json                 # Angular configuration
└── README.md                        # This file
```

## Getting Started

### Prerequisites
- Modern web browser with microphone access
- Node.js (for development)

### Installation
```bash
cd voice-recorder
npm install
```

### Running the Application
```bash
npm start
# or
npm run dev
```

The application will open at `http://localhost:8080`

### Using the Recorder

1. **Click "Start Recording"** - Grants microphone permission
2. **Speak normally** - The app detects voice vs. silence
3. **Automatic segmentation** - New recordings created after 4 seconds of silence
4. **Visual feedback** - Silence timer shows countdown
5. **Download options** - Individual segments or all recordings

## Technical Details

### Supported Formats
- **Recording**: WebM with Opus codec
- **Download**: WebM files with timestamps

### Browser Compatibility
- Chrome 47+
- Firefox 29+
- Safari 14.1+
- Edge 79+

### Performance
- **Real-time processing**: 100ms analysis intervals
- **Low latency**: Optimized for live recording
- **Memory efficient**: Streaming audio chunks

## Use Cases

- **Interviews**: Automatic pause detection between questions/answers
- **Meeting Notes**: Segment by speaker pauses
- **Voice Memos**: Natural break detection
- **Language Learning**: Practice with automatic segmentation
- **Podcasting**: Pre-segmented content creation

## Troubleshooting

### Microphone Issues
- Ensure browser permissions are granted
- Check system microphone settings
- Try refreshing the page

### Sensitivity Adjustment
Modify thresholds in the code for different environments:
- Increase `VOICE_THRESHOLD` for noisy environments
- Decrease `SILENCE_DURATION` for faster segmentation
- Adjust `NOISE_GATE_THRESHOLD` for ambient noise levels
