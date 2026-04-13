import { Injectable } from '@angular/core';
import { MatDialog, MatDialogRef } from '@angular/material/dialog';
import { FullscreenLoaderComponent } from './fullscreen-loader/fullscreen-loader.component';

export interface LoaderConfig {
  message?: string;
}

@Injectable({
  providedIn: 'root',
})
export class FullscreenLoaderService {
  private dialogRef: MatDialogRef<FullscreenLoaderComponent> | null = null;

  constructor(private dialog: MatDialog) { }

  show(config: LoaderConfig = {}): void {
    if (this.dialogRef) {
      this.dialogRef.componentInstance.data = { message: config.message };
      return;
    }

    this.dialogRef = this.dialog.open(FullscreenLoaderComponent, {
      width: '100vw',
      height: '100vh',
      maxWidth: '100vw',
      maxHeight: '100vh',
      panelClass: ['fullscreen-dialog'],
      disableClose: true,
      hasBackdrop: false,
      data: { message: config.message || 'Generating image...' }
    });
  }

  hide(): void {
    if (this.dialogRef) {
      this.dialogRef.close();
      this.dialogRef = null;
    }
  }

  isVisible(): boolean {
    return !!this.dialogRef;
  }
}
