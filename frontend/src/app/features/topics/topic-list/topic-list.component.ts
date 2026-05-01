import { NgOptimizedImage } from '@angular/common';
import { Component, inject, OnInit } from '@angular/core';
import { MatButtonModule } from "@angular/material/button";
import { MatCardModule } from '@angular/material/card';
import { MatDialog } from '@angular/material/dialog';
import { MatIconModule } from "@angular/material/icon";
import { MatMenuModule } from '@angular/material/menu';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatTooltip } from "@angular/material/tooltip";
import { RouterModule } from "@angular/router";
import { BottomNavComponent } from '../../../core/bottom-nav/bottom-nav.component';
import { FullscreenLoaderService } from '../../../shared/fullscreen-loader.service';
import { SimpleDialogComponent } from '../../../shared/simple-dialog/simple-dialog.component';
import { Topic, TopicService } from '../topic.service';


@Component({
    selector: 'app-topic-list',
    imports: [
        NgOptimizedImage,
        MatCardModule,
        MatButtonModule,
        MatIconModule,
        RouterModule,
        MatTooltip,
        BottomNavComponent,
        MatMenuModule,
    ],
    templateUrl: './topic-list.component.html',
    styleUrl: './topic-list.component.scss',
})
export class TopicListComponent implements OnInit {
    public topics!: Topic[];

    topicService = inject(TopicService);
    snackBar = inject(MatSnackBar);
    dialog = inject(MatDialog);
    loader = inject(FullscreenLoaderService);

    ngOnInit(): void {
        this.topicService.getAll().subscribe(topics => {
            this.topics = topics;
        });
    }

    edit(topicId: string): void {
        this.snackBar.open($localize`Not implemented yet. Please try again later.`, $localize`Close`, { duration: 5000 });
    }

    delete(topicId: string): void {
        this.dialog.open(SimpleDialogComponent, {
            data: {
                title: $localize`Deleting topic ...`,
                message: $localize`Are you sure you want to delete this topic? This action cannot be undone.`,
                confirm: true
            }
        }).afterClosed().subscribe(result => {
            if (result) {
                this.loader.show({ message: $localize`Deleting topic ...` })
                this.topicService.delete(topicId).subscribe({
                    complete: () => {
                        this.loader.hide()
                        this.topics = this.topics.filter(t => t.id !== topicId);
                        this.snackBar.open($localize`Topic deleted`, $localize`Ok`, { duration: 2000 })
                    },
                    error: err => {
                        this.loader.hide();
                        console.error('Failed to delete topic', err);
                        this.snackBar.open($localize`Failed to delete topic. Please try again later.`, $localize`Close`, { duration: 5000 });
                    }
                })
            }
        });
    }

}
