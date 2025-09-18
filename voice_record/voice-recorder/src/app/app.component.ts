import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="container">
      <h1>Voice Recorder</h1>
      <div class="status">
        {{ status }}
      </div>

      <div *ngIf="recordingCount > 0" class="recording-count">
        Recordings created: {{ recordingCount }}
      </div>

      <button
        class="record-button"
        [class.recording]="isRecording"
        (click)="toggleRecording()"
        [disabled]="!isSupported">
        {{ isRecording ? 'Stop Recording' : 'Start Recording' }}
      </button>

      <div *ngIf="silenceTimer > 0 && isRecording" class="silence-timer">
        Silence detected: {{ silenceTimer }}s (will create new recording)
      </div>

      <div class="audio-controls" *ngIf="audioBlobs.length > 0">
        <h3>Recorded Audio Segments:</h3>
        <div *ngFor="let blob of audioBlobs; let i = index" class="audio-segment">
          <p>Recording {{ i + 1 }} - {{ (blob.size / 1024).toFixed(1) }} KB</p>
          <audio controls [src]="getBlobUrl(blob)"></audio>
          <button class="record-button small" (click)="downloadBlob(blob, i)">Download</button>
        </div>
        <br>
        <button class="record-button" (click)="downloadAllRecordings()">Download All</button>
        <button class="record-button" (click)="clearAllRecordings()">Clear All</button>
      </div>

      <div *ngIf="!isSupported" class="error">
        Your browser doesn't support audio recording.
      </div>
    </div>
  `
})
export class AppComponent implements OnInit, OnDestroy {
  isRecording = false;
  isSupported = false;
  status = 'Ready to record';
  audioUrl: string | null = null;
  silenceTimer = 0;
  recordingCount = 0;
  audioBlobs: Blob[] = [];

  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];
  private stream: MediaStream | null = null;
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private silenceTimeout: any = null;
  private volumeCheckInterval: any = null;
  private isLoopMode = true;
  
  // Noise gate settings
  private readonly SILENCE_THRESHOLD = -50; // dB
  private readonly SILENCE_DURATION = 4000; // 4 seconds
  private readonly NOISE_GATE_THRESHOLD = -60; // dB for noise gate
  
  ngOnInit() {
    this.checkBrowserSupport();
  }
  
  ngOnDestroy() {
    this.cleanup();
  }
  
  private checkBrowserSupport() {
    this.isSupported = !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
    if (!this.isSupported) {
      this.status = 'Browser not supported';
    }
  }
  
  async toggleRecording() {
    if (this.isRecording) {
      this.stopRecordingCompletely();
    } else {
      await this.startRecording();
    }
  }
  
  private async startRecording() {
    try {
      this.status = 'Requesting microphone access...';
      
      // Request microphone access with noise suppression
      this.stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 44100
        }
      });
      
      // Set up audio context for volume analysis
      this.setupAudioAnalysis();
      
      // Set up MediaRecorder
      this.mediaRecorder = new MediaRecorder(this.stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      this.audioChunks = [];
      
      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data);
        }
      };
      
      this.mediaRecorder.onstop = () => {
        this.createAudioBlob();
      };
      
      this.mediaRecorder.start(100); // Collect data every 100ms
      this.isRecording = true;
      this.status = 'Recording in loop mode... (new recording every 4 seconds of silence)';

      // Start monitoring for silence
      this.startSilenceDetection();
      
    } catch (error) {
      console.error('Error starting recording:', error);
      this.status = 'Error accessing microphone';
    }
  }
  
  private setupAudioAnalysis() {
    this.audioContext = new AudioContext();
    this.analyser = this.audioContext.createAnalyser();
    this.analyser.fftSize = 512;
    this.analyser.smoothingTimeConstant = 0.3;
    
    if (this.stream) {
      const source = this.audioContext.createMediaStreamSource(this.stream);
      source.connect(this.analyser);
    }
  }
  
  private startSilenceDetection() {
    this.volumeCheckInterval = setInterval(() => {
      if (this.analyser) {
        const volume = this.getVolumeLevel();
        
        if (volume < this.SILENCE_THRESHOLD) {
          // Silence detected
          if (this.silenceTimeout === null) {
            this.startSilenceTimer();
          }
        } else {
          // Voice detected, reset silence timer
          this.resetSilenceTimer();
        }
      }
    }, 100);
  }
  
  private getVolumeLevel(): number {
    if (!this.analyser) return -100;
    
    const bufferLength = this.analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    this.analyser.getByteFrequencyData(dataArray);
    
    let sum = 0;
    for (let i = 0; i < bufferLength; i++) {
      sum += dataArray[i];
    }
    
    const average = sum / bufferLength;
    // Convert to dB
    return 20 * Math.log10(average / 255);
  }
  
  private startSilenceTimer() {
    this.silenceTimer = 0;

    const timerInterval = setInterval(() => {
      this.silenceTimer++;

      if (this.silenceTimer >= 4) {
        clearInterval(timerInterval);
        this.createNewRecordingSegment();
      }
    }, 1000);

    this.silenceTimeout = setTimeout(() => {
      clearInterval(timerInterval);
      this.createNewRecordingSegment();
    }, this.SILENCE_DURATION);
  }
  
  private resetSilenceTimer() {
    if (this.silenceTimeout) {
      clearTimeout(this.silenceTimeout);
      this.silenceTimeout = null;
    }
    this.silenceTimer = 0;
  }
  
  private createNewRecordingSegment() {
    console.log('createNewRecordingSegment called. MediaRecorder state:', this.mediaRecorder?.state);

    if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
      console.log('Stopping current recording segment...');
      // Stop current silence detection
      this.stopSilenceDetection();
      this.mediaRecorder.stop();
      this.status = 'Creating recording segment...';
    } else {
      console.log('MediaRecorder not in recording state, cannot create new segment');
    }
  }

  private stopSilenceDetection() {
    if (this.silenceTimeout) {
      clearTimeout(this.silenceTimeout);
      this.silenceTimeout = null;
    }

    if (this.volumeCheckInterval) {
      clearInterval(this.volumeCheckInterval);
      this.volumeCheckInterval = null;
    }

    this.silenceTimer = 0;
  }

  private stopRecordingCompletely() {
    if (this.mediaRecorder && this.isRecording) {
      this.mediaRecorder.stop();
      this.isRecording = false;
      this.status = `Recording stopped! Created ${this.recordingCount} segments`;
      this.cleanup();
    }
  }

  private createAudioBlob() {
    console.log('createAudioBlob called. isRecording:', this.isRecording, 'audioChunks.length:', this.audioChunks.length);

    if (this.audioChunks.length > 0) {
      const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
      this.audioBlobs.push(audioBlob);
      this.recordingCount++;

      console.log(`Audio blob ${this.recordingCount} created:`, audioBlob, 'Size:', audioBlob.size);

      // Reset for next recording segment
      this.audioChunks = [];

      if (this.isRecording) {
        console.log('Still recording, starting new segment...');
        // Continue recording if still in recording mode
        this.startNewSegment();
      } else {
        console.log('Recording stopped, not starting new segment');
      }
    } else {
      console.log('No audio chunks to create blob from');
    }
  }

  private async startNewSegment() {
    console.log('startNewSegment called. isRecording:', this.isRecording, 'stream exists:', !!this.stream);

    try {
      if (this.stream && this.isRecording) {
        console.log('Starting new segment after 100ms delay...');

        // Wait a bit before starting new segment
        setTimeout(() => {
          console.log('Timeout callback executed. isRecording:', this.isRecording);

          if (this.isRecording) {
            console.log('Creating new MediaRecorder...');

            this.mediaRecorder = new MediaRecorder(this.stream, {
              mimeType: 'audio/webm;codecs=opus'
            });

            this.mediaRecorder.ondataavailable = (event) => {
              if (event.data.size > 0) {
                this.audioChunks.push(event.data);
              }
            };

            this.mediaRecorder.onstop = () => {
              console.log('MediaRecorder stopped, calling createAudioBlob');
              this.createAudioBlob();
            };

            this.mediaRecorder.start(100);
            console.log('MediaRecorder started for segment', this.recordingCount + 1);
            this.status = `Recording segment ${this.recordingCount + 1}... (new recording every 4 seconds of silence)`;

            // Restart silence detection for the new segment
            console.log('Restarting silence detection...');
            this.startSilenceDetection();
          } else {
            console.log('Recording stopped during timeout, not starting new segment');
          }
        }, 100);
      } else {
        console.log('Cannot start new segment - stream or recording state invalid');
      }
    } catch (error) {
      console.error('Error starting new segment:', error);
    }
  }
  
  private cleanup() {
    this.stopSilenceDetection();

    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
    }

    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }

    this.analyser = null;
  }
  
  getBlobUrl(blob: Blob): string {
    return URL.createObjectURL(blob);
  }

  downloadBlob(blob: Blob, index: number) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `recording-${index + 1}-${new Date().getTime()}.webm`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  downloadAllRecordings() {
    this.audioBlobs.forEach((blob, index) => {
      this.downloadBlob(blob, index);
    });
  }

  clearAllRecordings() {
    this.audioBlobs = [];
    this.recordingCount = 0;
    this.status = 'Ready to record';
  }
}