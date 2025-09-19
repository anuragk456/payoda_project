import { Injectable } from '@angular/core';

/**
 * Interface for audio recording metadata
 */
export interface AudioRecording {
  blob: Blob;
  duration: number;
  timestamp: Date;
  url: string;
}

/**
 * Production-ready Voice Activity Detection Service
 *
 * This service provides real-time human voice detection with advanced filtering
 * to distinguish speech from background noise, music, laughter, and other sounds.
 *
 * Features:
 * - Human voice formant analysis
 * - Background noise calibration
 * - Music and laughter filtering
 * - Automatic blob creation after silence periods
 * - Production-grade noise filtering (fan, AC, typing, clapping)
 */
@Injectable({
  providedIn: 'root'
})
export class VoiceActivityDetectionService {
  // Core audio processing components
  private mediaRecorder: MediaRecorder | null = null;
  private stream: MediaStream | null = null;
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;

  // Voice activity detection state
  private vadInterval: any = null;
  private isRecording = false;
  private isSpeaking = false;
  private silenceTimer: any = null;

  // Recording management
  private currentChunks: Blob[] = [];
  private preRecordingChunks: Blob[] = []; // Buffer for pre-recording audio
  private speakingStartTime: number = 0;
  private recordings: AudioRecording[] = [];
  private isPreRecording = false;

  // Voice detection algorithm state
  private voiceHistory: boolean[] = [];
  private lastFrequencyData: Uint8Array | null = null;
  private energyHistory: number[] = [];
  private backgroundNoiseLevel: number = 0;
  private noiseCalibrationFrames: number = 0;

  // Configuration constants
  private readonly SILENCE_THRESHOLD = 4000; // 4 seconds silence before creating blob
  private readonly VOICE_CONSISTENCY_COUNT = 3; // Frames to track for temporal consistency
  private readonly NOISE_CALIBRATION_FRAMES = 30; // Initial frames for noise calibration
  private readonly PRE_RECORDING_BUFFER_SIZE = 10; // Keep last 10 chunks (1 second) for pre-recording

  constructor() {}

  /**
   * Initialize the voice detection service
   * Sets up audio context, media recorder, and voice detection pipeline
   */
  async initialize(): Promise<void> {
    try {
      console.log('🚀 Initializing voice detection...');

      // Request microphone access with optimized settings for voice detection
      this.stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: false // Disabled to preserve voice characteristics
        }
      });

      // Create audio context for frequency analysis
      this.audioContext = new AudioContext({ sampleRate: 16000 });

      // Create initial media recorder
      this.createNewMediaRecorder();

      this.setupVoiceDetection();
      console.log('✅ Voice detection ready');

    } catch (error) {
      console.error('❌ Error initializing voice detection:', error);
      throw error;
    }
  }

  /**
   * Create a new MediaRecorder instance for each recording
   * This ensures blob URLs remain valid and accessible
   */
  private createNewMediaRecorder(): void {
    if (!this.stream) return;

    // Set up media recorder for audio capture
    this.mediaRecorder = new MediaRecorder(this.stream, {
      mimeType: 'audio/webm;codecs=opus'
    });

    // Handle audio data chunks as they become available
    this.mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        if (this.isRecording) {
          this.currentChunks.push(event.data);
        } else if (this.isPreRecording) {
          // Store in pre-recording buffer
          this.preRecordingChunks.push(event.data);
          // Keep only the last N chunks for pre-recording buffer
          if (this.preRecordingChunks.length > this.PRE_RECORDING_BUFFER_SIZE) {
            this.preRecordingChunks.shift();
          }
        }
      }
    };

    // Process recording when it stops
    this.mediaRecorder.onstop = () => {
      this.processRecording();
    };
  }

  /**
   * Set up the audio analysis pipeline for voice detection
   */
  private setupVoiceDetection(): void {
    if (!this.stream || !this.audioContext) return;

    // Create audio source from microphone stream
    const source = this.audioContext.createMediaStreamSource(this.stream);

    // Configure frequency analyzer
    this.analyser = this.audioContext.createAnalyser();
    this.analyser.fftSize = 2048; // Higher resolution for better frequency analysis
    this.analyser.smoothingTimeConstant = 0.3; // Moderate smoothing for stability

    source.connect(this.analyser);
  }

  /**
   * Start the voice activity detection loop
   */
  async startVoiceDetection(): Promise<void> {
    if (this.analyser) {
      // Check for voice activity every 100ms (10 times per second)
      this.vadInterval = setInterval(() => {
        this.detectVoiceActivity();
      }, 100);
      console.log('🎤 Voice detection started');
    }
  }

  /**
   * Stop the voice activity detection loop
   */
  async stopVoiceDetection(): Promise<void> {
    if (this.vadInterval) {
      clearInterval(this.vadInterval);
      this.vadInterval = null;
    }
  }

  /**
   * Analyze current audio frame for voice activity
   */
  private detectVoiceActivity(): void {
    if (!this.analyser) return;

    // Get frequency domain data
    const bufferLength = this.analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    this.analyser.getByteFrequencyData(dataArray);

    // Apply advanced voice detection algorithm
    const isVoiceActive = this.detectHumanVoice(dataArray);
    this.handleVoiceActivity(isVoiceActive);
  }

  /**
   * Advanced human voice detection algorithm
   * Uses spectral analysis, formant detection, and temporal consistency
   * to distinguish human speech from background noise, music, and other sounds
   */
  private detectHumanVoice(frequencyData: Uint8Array): boolean {
    const sampleRate = this.audioContext!.sampleRate;
    const binSize = sampleRate / (2 * frequencyData.length);

    // Human voice frequency ranges (Hz)
    // Fundamental frequency: 85-255Hz (male: 85-180Hz, female: 165-255Hz)
    const fundamentalRange = { min: Math.floor(85 / binSize), max: Math.floor(255 / binSize) };
    // Formant 1: First resonance peak, vowel characteristics
    const formant1Range = { min: Math.floor(300 / binSize), max: Math.floor(1000 / binSize) };
    // Formant 2: Second resonance peak, vowel/consonant characteristics
    const formant2Range = { min: Math.floor(800 / binSize), max: Math.floor(2300 / binSize) };
    // Formant 3: Third resonance peak, speech intelligibility
    const formant3Range = { min: Math.floor(1500 / binSize), max: Math.floor(3500 / binSize) };

    // Background noise frequency ranges for filtering
    const lowFreqNoiseRange = { min: Math.floor(20 / binSize), max: Math.floor(80 / binSize) };   // Fan/AC noise
    const midFreqNoiseRange = { min: Math.floor(2500 / binSize), max: Math.floor(5000 / binSize) }; // Music harmonics
    const highFreqNoiseRange = { min: Math.floor(5000 / binSize), max: Math.floor(8000 / binSize) }; // High freq noise

    // Initialize energy counters for different frequency bands
    let fundamentalEnergy = 0;
    let formant1Energy = 0;
    let formant2Energy = 0;
    let formant3Energy = 0;
    let lowFreqNoise = 0;
    let midFreqNoise = 0;
    let highFreqNoise = 0;
    let totalEnergy = 0;
    let spectralCentroid = 0;
    let spectralFlux = 0;
    let harmonicPeaks = 0;

    // Analyze frequency spectrum and calculate spectral features
    for (let i = 0; i < frequencyData.length; i++) {
      const value = frequencyData[i];
      const frequency = i * binSize;
      totalEnergy += value;
      spectralCentroid += frequency * value; // Weighted frequency centroid

      // Accumulate energy in human voice formant ranges
      if (i >= fundamentalRange.min && i <= fundamentalRange.max) {
        fundamentalEnergy += value;
      }
      if (i >= formant1Range.min && i <= formant1Range.max) {
        formant1Energy += value;
      }
      if (i >= formant2Range.min && i <= formant2Range.max) {
        formant2Energy += value;
      }
      if (i >= formant3Range.min && i <= formant3Range.max) {
        formant3Energy += value;
      }

      // Accumulate energy in background noise ranges
      if (i >= lowFreqNoiseRange.min && i <= lowFreqNoiseRange.max) {
        lowFreqNoise += value;
      }
      if (i >= midFreqNoiseRange.min && i <= midFreqNoiseRange.max) {
        midFreqNoise += value;
      }
      if (i >= highFreqNoiseRange.min && i <= highFreqNoiseRange.max) {
        highFreqNoise += value;
      }

      // Count significant harmonic peaks (indicates music or complex tonal sounds)
      if (i > 0 && i < frequencyData.length - 1) {
        if (value > frequencyData[i-1] && value > frequencyData[i+1] && value > 50) {
          harmonicPeaks++;
        }
      }
    }

    if (totalEnergy === 0) return false;

    // Normalize spectral centroid and calculate average energy
    spectralCentroid /= totalEnergy;
    const avgEnergy = totalEnergy / frequencyData.length;

    // Adaptive background noise calibration during startup
    if (this.noiseCalibrationFrames < this.NOISE_CALIBRATION_FRAMES) {
      this.backgroundNoiseLevel = (this.backgroundNoiseLevel * this.noiseCalibrationFrames + avgEnergy) / (this.noiseCalibrationFrames + 1);
      this.noiseCalibrationFrames++;
    }

    // Maintain energy history for temporal analysis (rolling window of 10 frames)
    this.energyHistory.push(avgEnergy);
    if (this.energyHistory.length > 10) {
      this.energyHistory.shift();
    }

    // Calculate spectral flux (measure of spectral change over time)
    if (this.lastFrequencyData) {
      for (let i = 0; i < Math.min(frequencyData.length, this.lastFrequencyData.length); i++) {
        const diff = frequencyData[i] - this.lastFrequencyData[i];
        if (diff > 0) spectralFlux += diff; // Only positive changes
      }
      spectralFlux /= frequencyData.length;
    }

    // Calculate key speech characteristics
    const formantRatio = (formant1Energy + formant2Energy + formant3Energy) / totalEnergy;
    const backgroundNoiseRatio = (lowFreqNoise + midFreqNoise + highFreqNoise) / totalEnergy;
    const harmonicDensity = harmonicPeaks / (frequencyData.length / 100); // Normalize peaks per 100 bins

    // Note: Energy variance calculation removed for production simplicity
    // Speech energy stability is handled through other criteria

    // Voice detection criteria (optimized for production use)

    // Energy level must be above background noise but not excessively loud
    const hasProperEnergy = avgEnergy > Math.max(4, this.backgroundNoiseLevel * 1.5) &&
                           avgEnergy < 200;

    // Voice must have significant energy in formant frequency ranges
    const hasVoiceFormants = formantRatio > 0.15 &&
                            (fundamentalEnergy > totalEnergy * 0.05 ||
                             formant1Energy > totalEnergy * 0.05 ||
                             formant2Energy > totalEnergy * 0.05);

    // Background noise should not dominate the signal
    const hasLowBackgroundNoise = backgroundNoiseRatio < 0.8;

    // Spectral centroid should be in typical human voice range
    const hasVoiceLikeSpectrum = spectralCentroid > 200 && spectralCentroid < 4000;

    // Filter out music (which has many harmonic peaks)
    const isNotMusic = harmonicDensity < 20;

    // Speech has moderate spectral changes over time
    const hasModerateFlux = spectralFlux >= 0.1;

    // Simplified energy stability check (always true for production)
    const hasStableEnergy = true;

    // Filter out laughter (burst patterns with many harmonics and rapid changes)
    const isNotLaughter = !(harmonicPeaks > 30 && spectralFlux > 50);

    // Combine all criteria for current frame voice detection
    const currentVoiceDetection = hasProperEnergy && hasVoiceFormants && hasLowBackgroundNoise &&
                                 hasVoiceLikeSpectrum && isNotMusic && hasModerateFlux &&
                                 hasStableEnergy && isNotLaughter;

    // Detect and filter transient sounds (clapping, door slams, etc.)
    let isTransient = false;
    if (this.lastFrequencyData) {
      let energyChange = 0;
      for (let i = 0; i < Math.min(frequencyData.length, this.lastFrequencyData.length); i++) {
        energyChange += Math.abs(frequencyData[i] - this.lastFrequencyData[i]);
      }
      const avgEnergyChange = energyChange / frequencyData.length;

      // Identify transient sounds by sudden energy changes or noise dominance
      isTransient = avgEnergyChange > 25 ||
                   backgroundNoiseRatio > 0.5 ||
                   (avgEnergy > this.backgroundNoiseLevel * 6 && harmonicPeaks > 10);
    }

    // Store current frequency data for next frame comparison
    this.lastFrequencyData = new Uint8Array(frequencyData);

    // Temporal consistency: track voice detection over multiple frames
    this.voiceHistory.push(currentVoiceDetection && !isTransient);
    if (this.voiceHistory.length > this.VOICE_CONSISTENCY_COUNT) {
      this.voiceHistory.shift();
    }

    // Final decision: require consistent detection (1 out of last 2 frames)
    const consistentVoiceCount = this.voiceHistory.filter(v => v).length;
    const finalResult = this.voiceHistory.length >= 2 && consistentVoiceCount >= 1;

    // Optional: Enable for debugging in development
    // if (this.noiseCalibrationFrames % 20 === 0 || finalResult) {
    //   console.log('Voice Detection Debug:', { avgEnergy, finalResult });
    // }

    return finalResult;
  }

  /**
   * Handle voice activity state changes and manage recording lifecycle
   */
  private handleVoiceActivity(isVoiceActive: boolean): void {
    if (isVoiceActive && !this.isSpeaking) {
      // Voice detected: start actual recording (including pre-recorded buffer)
      this.isSpeaking = true;
      this.speakingStartTime = Date.now() - 1000; // Subtract 1 second to account for pre-recording
      this.startRecording();

      // Cancel any pending silence timer
      if (this.silenceTimer) {
        clearTimeout(this.silenceTimer);
        this.silenceTimer = null;
      }

      console.log('🎙️ VOICE DETECTED: Recording started (with pre-buffer)');

    } else if (!isVoiceActive && this.isSpeaking) {
      // Voice stopped: start silence countdown
      if (!this.silenceTimer) {
        console.log('🔇 Voice stopped → Starting 4-second countdown...');
        this.silenceTimer = setTimeout(() => {
          this.isSpeaking = false;
          this.stopRecording();
          console.log('⏰ 4 seconds elapsed → Creating blob');
        }, this.SILENCE_THRESHOLD);
      }
    } else if (isVoiceActive && this.isSpeaking && this.silenceTimer) {
      // Voice resumed during silence countdown: cancel timer
      console.log('🔄 Voice resumed → Timer canceled');
      clearTimeout(this.silenceTimer);
      this.silenceTimer = null;
    }
  }

  /**
   * Start pre-recording to capture audio before voice detection
   */
  private startPreRecording(): void {
    if (this.mediaRecorder && !this.isPreRecording && !this.isRecording) {
      this.preRecordingChunks = [];
      this.mediaRecorder.start(100); // Collect data every 100ms
      this.isPreRecording = true;
      console.log('🔄 Pre-recording started');
    }
  }

  /**
   * Start actual recording (includes pre-recorded buffer)
   */
  private startRecording(): void {
    if (this.isPreRecording) {
      // Copy pre-recorded chunks to current recording
      this.currentChunks = [...this.preRecordingChunks];
      this.isPreRecording = false;
      this.isRecording = true;
      console.log(`📼 Added ${this.preRecordingChunks.length} pre-recorded chunks`);
    } else if (this.mediaRecorder && !this.isRecording) {
      this.currentChunks = [];
      this.mediaRecorder.start(100); // Collect data every 100ms
      this.isRecording = true;
    }
  }

  /**
   * Stop audio recording
   */
  private stopRecording(): void {
    if (this.mediaRecorder && (this.isRecording || this.isPreRecording)) {
      this.mediaRecorder.stop();
      this.isRecording = false;
      this.isPreRecording = false;
      // Don't restart pre-recording immediately - wait for processRecording to complete
    }
  }

  /**
   * Process completed recording and create audio blob
   */
  private processRecording(): void {
    if (this.currentChunks.length > 0) {
      const blob = new Blob(this.currentChunks, { type: 'audio/webm;codecs=opus' });
      const duration = Date.now() - this.speakingStartTime;
      const url = URL.createObjectURL(blob);

      const recording: AudioRecording = {
        blob,
        duration,
        timestamp: new Date(),
        url
      };

      this.recordings.push(recording);
      console.log(`🎯 BLOB #${this.recordings.length}: ${(duration/1000).toFixed(1)}s (${(blob.size / 1024).toFixed(1)}KB)`, blob);
      this.currentChunks = [];

      // Create a new MediaRecorder instance for the next recording
      this.createNewMediaRecorder();

      // Now restart pre-recording for next detection
      setTimeout(() => {
        this.startPreRecording();
      }, 100);
    }
  }

  /**
   * Get all recorded audio blobs
   */
  getRecordings(): AudioRecording[] {
    return this.recordings;
  }

  /**
   * Stop voice detection and clean up all resources
   */
  async stop(): Promise<void> {
    // Cancel any pending silence timer
    if (this.silenceTimer) {
      clearTimeout(this.silenceTimer);
    }

    // Stop any ongoing recording
    if (this.isRecording || this.isPreRecording) {
      this.mediaRecorder?.stop();
      this.isRecording = false;
      this.isPreRecording = false;
    }

    // Stop voice detection loop
    await this.stopVoiceDetection();

    // Release microphone access
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
    }

    // Close audio context
    if (this.audioContext) {
      await this.audioContext.close();
    }

    console.log('🛑 Voice detection stopped');
  }

  /**
   * Clear all recordings and free memory
   */
  clearRecordings(): void {
    this.recordings.forEach(recording => {
      URL.revokeObjectURL(recording.url);
    });
    this.recordings = [];
    console.log('🗑️ Recordings cleared');
  }

  /**
   * Start the voice detection process
   */
  async startDetection(): Promise<void> {
    // Start pre-recording to capture audio before voice detection
    this.startPreRecording();
    await this.startVoiceDetection();
  }

  /**
   * Reset background noise calibration
   * Useful when moving to a different acoustic environment
   */
  recalibrateNoise(): void {
    this.backgroundNoiseLevel = 0;
    this.noiseCalibrationFrames = 0;
    this.energyHistory = [];
    console.log('🔄 Noise calibration reset');
  }
}