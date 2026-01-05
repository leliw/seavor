import { Component, Inject } from '@angular/core';
import { MatDialogModule, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';


export interface DialogData {
    title: string;
    message: string;
    confirm: boolean;
}

@Component({
    selector: 'app-simple-dialog',
    imports: [MatDialogModule, MatButtonModule],
    templateUrl: './simple-dialog.component.html',
    styleUrl: './simple-dialog.component.scss'
})
export class SimpleDialogComponent {

    constructor(
        public dialogRef: MatDialogRef<SimpleDialogComponent>,
        @Inject(MAT_DIALOG_DATA) public data: DialogData
    ) { }

    onConfirm(): void {
        this.dialogRef.close(true);
    }

    onCancel(): void {
        this.dialogRef.close(false);
    }

}