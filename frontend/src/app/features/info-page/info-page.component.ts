import { Component, effect, inject, input, output } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatButtonModule } from '@angular/material/button';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatIconModule } from "@angular/material/icon";
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { InfoPage, InfoPageService } from './info-page.service';
import { CommonModule } from '@angular/common';
import { MatToolbarModule } from "@angular/material/toolbar";
import { MatListModule } from "@angular/material/list";
import { RouterModule } from '@angular/router';
import { MarkdownPipe } from "../../shared/markdown.pipe";


@Component({
    selector: 'app-info-page',
    imports: [
    CommonModule,
    RouterModule,
    MatExpansionModule,
    MatButtonModule,
    MatIconModule,
    MatToolbarModule,
    MatListModule,
    MarkdownPipe,
    MatSnackBarModule
],
    templateUrl: './info-page.component.html',
    styleUrl: './info-page.component.scss',
})
export class InfoPageComponent {

    topicId = input.required<string>();
    id = input.required<string>();

    previousPage = output<void>();
    nextPage = output<void>();

    public page!: InfoPage;
    public showHint: boolean = false;
    public native: boolean = false;
    
    private service = inject(InfoPageService);
    private snackBar = inject(MatSnackBar);

    constructor() {
        effect(() => {
            const topicId = this.topicId();
            const id = this.id();
            this.service.get(topicId, id).subscribe({
                next: p => {
                    this.page = p;
                },
                error: err => {
                    console.error('Failed to load info page', err);
                    this.snackBar.open($localize`Failed to load info page. Please try again later.`, $localize`Close`, { duration: 5000 });
                }
            });
        });
    }

}
