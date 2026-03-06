import { Component, effect, inject, input, output } from '@angular/core';
import { DefinitionGuessExercise, DefinitionGuessService, NativeSentence, Sentence } from './definition-guess.service';
import { BottomNavComponent } from "../../core/bottom-nav/bottom-nav.component";
import { EvaluationBarComponent } from "../../core/evaluation-bar/evaluation-bar.component";

@Component({
    selector: 'app-definition-guess',
    imports: [
        BottomNavComponent,
        EvaluationBarComponent
    ],
    templateUrl: './definition-guess.component.html',
    styleUrl: './definition-guess.component.scss',
})
export class DefinitionGuessComponent {
    topicId = input.required<string>();
    id = input.required<string>();
    private service = inject(DefinitionGuessService);

    previousPage = output<void>();
    nextPage = output<void>();

    public exercise!: DefinitionGuessExercise;

    public sentence!: Sentence;
    public nativeSentence?: NativeSentence;
    public showHint: boolean = false;
    public native: boolean = false;
    public showAnswer: boolean = false;
    public answer: string | null = null;

    constructor() {
        effect(() => {
            const topicId = this.topicId();
            const id = this.id();
            this.service.get(topicId, id).subscribe(e => {
                this.answer = null;
                this.exercise = e;
                const sentenceIndex = Math.floor(Math.random() * this.exercise.sentences.length)
                this.sentence = this.exercise.sentences[sentenceIndex];
                this.nativeSentence = this.exercise.native_sentences ? this.exercise.native_sentences[sentenceIndex] : undefined;
                this.showHint = false;
                this.native = false;
            })
        });
    }

    check(): void {
        this.answer = this.sentence.text_with_gap.replace(/_{3,}/g, '<b>' + this.sentence.gap_filler_form + '</b>');
        this.showAnswer = true;
    }

    onEvaluation(evaluation: number): void {
        console.log(evaluation);
        this.showAnswer = false;
        this.showHint = false;
        this.nextPage.emit();
    }

}
