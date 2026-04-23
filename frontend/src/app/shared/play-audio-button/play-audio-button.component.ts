import { Component, effect, input, OnDestroy, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-play-audio-button',
  imports: [
    MatButtonModule,
    MatIconModule,

  ],
  templateUrl: './play-audio-button.component.html',
})
export class PlayAudioButtonComponent implements OnDestroy {
  srcUrl = input.required<string>();
  autoPlay = input<boolean>(false);

  audio: HTMLAudioElement = new Audio();
  isPlaying = signal<boolean>(false);

  constructor() {
    effect(() => {
      this.audio.src = this.srcUrl();
      this.audio.load();
      this.audio.onended = () => this.isPlaying.set(false);
      if (this.autoPlay()) {
        this.play();
      }
    });
  }


  play(): Promise<void> {
    return new Promise((resolve) => {
      this.audio.play().catch(err => console.error('Audio play error:', err));
      this.isPlaying.set(true);
      setTimeout(() => {
        this.audio.pause();
        this.audio.currentTime = 0;
        setTimeout(() => {
          this.audio.play().catch(err => console.error('Audio play error:', err));
          this.audio.onended = () => {
            this.isPlaying.set(false);
            resolve();
            this.audio.onended = () => this.isPlaying.set(false);
          }
        }, 250);
      }, 250);
    });
  }

  pause() {
    this.audio.pause();
    this.isPlaying.set(false);
  }

  ngOnDestroy(): void {
    this.audio.pause();
    this.audio.src = '';
  }
}
