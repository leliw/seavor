import { Component, inject, ChangeDetectionStrategy } from '@angular/core';
import { PageHeader, Topic, TopicService } from '../topic.service';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { GapFillChoiceComponent } from "../../gap-fill-choice/gap-fill-choice.component";
import { MatDialog } from '@angular/material/dialog';
import { SimpleDialogComponent } from '../../../shared/simple-dialog/simple-dialog.component';
import { InfoPageComponent } from "../../info-page/info-page.component";
import { DefinitionGuessComponent } from "../../definition-guess/definition-guess.component";
import { MatToolbarModule } from "@angular/material/toolbar";
import { MatIconModule } from "@angular/material/icon";
import { MatMenuModule } from "@angular/material/menu";
import { FullscreenLoaderService } from '../../../shared/fullscreen-loader.service';
import { PageService } from '../../pages/page.service';
import { MatButtonModule } from '@angular/material/button';

@Component({
    selector: 'app-topic-view',
    imports: [
    CommonModule,
    GapFillChoiceComponent,
    InfoPageComponent,
    DefinitionGuessComponent,
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
    MatMenuModule,
    RouterModule
],
    templateUrl: './topic-view.component.html',
    changeDetection: ChangeDetectionStrategy.Eager,
    styleUrl: './topic-view.component.scss',
})
export class TopicViewComponent {
    private dialog = inject(MatDialog);
    private router = inject(Router);
    private route = inject(ActivatedRoute);
    private topicService = inject(TopicService);
    private pageService = inject(PageService);

    public topicId!: string;
    public topic?: Topic;
    public pages!: PageHeader[];
    public page_no!: number;

    ngOnInit(): void {
        this.route.params.subscribe(params => {
            this.topicId = params['topic_id'];
            this.topicService.get(this.topicId).subscribe(topic => this.topic = topic)
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

    loader = inject(FullscreenLoaderService);

    addImage() {
        this.loader.show({ message: 'Generating & adding image...' });
        this.pageService.addImage(this.topicId, this.pages[this.page_no].id).subscribe({
            complete: () => this.loader.hide(),
            error: () => this.loader.hide()
        });
    }
}
