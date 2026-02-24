import { Component, inject } from '@angular/core';
import { PageHeader, TopicService } from '../topic.service';
import { ActivatedRoute, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { GapFillChoiceComponent } from "../../gap-fill-choice/gap-fill-choice.component";
import { MatDialog } from '@angular/material/dialog';
import { SimpleDialogComponent } from '../../../shared/simple-dialog/simple-dialog.component';

@Component({
    selector: 'app-topic-view',
    imports: [CommonModule, GapFillChoiceComponent],
    templateUrl: './topic-view.component.html',
    styleUrl: './topic-view.component.scss',
})
export class TopicViewComponent {
    private dialog = inject(MatDialog);
    private router = inject(Router);
    private route = inject(ActivatedRoute);
    private topicService = inject(TopicService);

    public topicId!: string;
    public pages!: PageHeader[];
    public page_no!: number;

    ngOnInit(): void {
        this.route.params.subscribe(params => {
            this.topicId = params['topic_id'];
            this.topicService.getPages(this.topicId).subscribe({
                next: pages => {
                    this.pages = pages.sort((a, b) => a.order - b.order);
                    this.page_no = 0
                },
                error: err => {
                    console.error('Failed to load topic pages', err);
                    this.dialog.open(SimpleDialogComponent, {
                        data: {
                            title: $localize`Error`,
                            message: $localize`Failed to load topic pages. Please try again later.`
                        }
                    }).afterClosed().subscribe(() => this.router.navigate(["/"]));
                }
            });
        });
    }

    onPreviousPage() {
        if (this.page_no > 0) {
            this.page_no -= 1;
        }
    }

    onNextPage() {
        if (this.page_no + 1 < this.pages.length) {
            this.page_no += 1;
        } else {
            this.dialog.open(SimpleDialogComponent, {
                data: {
                    title: $localize`Congratulations!`,
                    message: $localize`That's all!`
                }
            }).afterClosed().subscribe(() => this.router.navigate(["/"]));
        }
    }
}
