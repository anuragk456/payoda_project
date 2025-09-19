import { Component, OnDestroy } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';
import { VoiceActivityDetectionService, AudioRecording } from './services/voice-activity-detection.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App implements OnDestroy {
  isRecording = false;
  isInitializing = false;
  recordings: AudioRecording[] = [];
  currentStatus: 'idle' | 'listening' | 'speaking' | 'silence' = 'idle';

  constructor(private vadService: VoiceActivityDetectionService) {}

  async ngOnDestroy() {
    await this.vadService.stop();
  }

  async toggleRecording() {
    if (this.isRecording) {
      await this.vadService.stop();
      this.isRecording = false;
      this.currentStatus = 'idle';
    } else {
      this.isInitializing = true;
      try {
        await this.vadService.initialize();
        await this.vadService.startDetection();
        this.isRecording = true;
        this.currentStatus = 'listening';
        this.isInitializing = false;
        this.startRecordingPolling();
      } catch (error) {
        console.error('Failed to start recording:', error);
        this.isRecording = false;
        this.currentStatus = 'idle';
        this.isInitializing = false;
        alert('Failed to initialize voice detection.');
      }
    }
  }

  private startRecordingPolling() {
    const updateRecordings = () => {
      if (this.isRecording) {
        this.recordings = this.vadService.getRecordings();
        setTimeout(updateRecordings, 200);
      }
    };
    updateRecordings();
  }

  clearRecordings() {
    this.vadService.clearRecordings();
    this.recordings = [];
  }

  getStatusClass(): string {
    return this.currentStatus;
  }

  getStatusText(): string {
    switch (this.currentStatus) {
      case 'idle':
        return 'Ready for voice detection';
      case 'listening':
        return 'Listening for human speech...';
      case 'speaking':
        return 'Recording human voice';
      case 'silence':
        return 'Creating blob after silence';
      default:
        return 'Unknown status';
    }
  }

  formatDuration(ms: number): string {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;

    if (minutes > 0) {
      return `${minutes}m ${remainingSeconds}s`;
    }
    return `${seconds}s`;
  }

  formatTime(date: Date): string {
    return date.toLocaleTimeString();
  }

  downloadRecording(recording: AudioRecording, index: number) {
    const link = document.createElement('a');
    link.href = recording.url;
    link.download = `voice-recording-${index + 1}-${recording.timestamp.getTime()}.webm`;
    link.click();
  }
}
