import { CommonModule } from '@angular/common';
import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

@Component({
  selector: 'app-fullscreen-loader',
  imports: [
    CommonModule,
    MatDialogModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './fullscreen-loader.component.html',
  styleUrl: './fullscreen-loader.component.scss',
})
export class FullscreenLoaderComponent {
  constructor(
    @Inject(MAT_DIALOG_DATA) public data: { message?: string }
  ) { }
}
