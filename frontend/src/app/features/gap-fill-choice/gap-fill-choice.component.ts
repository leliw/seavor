import { Component, effect, inject, input, Input, OnInit, output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { MatIconModule } from "@angular/material/icon";
import { MatListModule } from "@angular/material/list";
import { MatRadioChange, MatRadioModule } from '@angular/material/radio';
import { MatToolbarModule } from "@angular/material/toolbar";
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { SimpleDialogComponent } from '../../shared/simple-dialog/simple-dialog.component';
import { GapFillChoiceExercise, GapFillChoiceService } from './gap-fill-choice.service';

@Component({
    selector: 'app-gap-fill-choice',
    imports: [
        RouterModule,
        MatRadioModule,
        FormsModule,
        MatToolbarModule,
        MatIconModule,
        MatListModule
    ],
    templateUrl: './gap-fill-choice.component.html',
    styleUrl: './gap-fill-choice.component.scss',
})
export class GapFillChoiceComponent implements OnInit {
    topicId = input.required<string>();
    id = input.required<string>();

    previousPage = output<void>();
    nextPage = output<void>();
    private router = inject(Router);
    private service = inject(GapFillChoiceService);
    private route = inject(ActivatedRoute);


    exercise!: GapFillChoiceExercise;

    native = false;
    showHint = false;
    disabledAnswer: boolean[] = [];
    answer: number | null = null;

    constructor() {
        effect(() => {
            const topicId = this.topicId();
            const id = this.id();
            this.service.get(topicId, id).subscribe(e => {
                this.answer = null;
                this.exercise = e;
                this.disabledAnswer = new Array(this.exercise.options.length).fill(false);
            })
        });
    }
    ngOnInit(): void {
    }

    private dialog = inject(MatDialog);

    onAnswer(event: MatRadioChange<any>) {
        if (event.value == this.exercise.correct_index) {
            const message = this.exercise.target_sentence.replace(this.exercise.gap_marker!, '<b>' + this.exercise.options[event.value] + '</b>');
            this.dialog.open(SimpleDialogComponent, {
                data: {
                    title: $localize`Correct`,
                    message: message,
                }
            }).afterClosed().subscribe(() => {
                this.nextPage.emit();
            });
        } else {
            var message = this.exercise.target_hint;
            if (this.exercise.target_distractors_explanation)
                message += "<br />\n<hr />\n" + this.exercise.target_distractors_explanation[event.value];
            this.dialog.open(SimpleDialogComponent, {
                data: {
                    title: $localize`Wrong`,
                    message: message,
                }
            }).afterClosed().subscribe(() => {
                this.disabledAnswer[event.value] = true;
                this.answer = null;
            });
        }
    }

}

