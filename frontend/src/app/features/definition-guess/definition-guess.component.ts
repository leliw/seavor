import { ChangeDetectorRef, Component, effect, inject, input, output, ViewChild } from '@angular/core';
import { DefinitionGuessExercise, DefinitionGuessService, NativeSentence, Sentence } from './definition-guess.service';
import { BottomNavComponent } from "../../core/bottom-nav/bottom-nav.component";
import { EvaluationBarComponent } from "../../core/evaluation-bar/evaluation-bar.component";
import { NgOptimizedImage } from '@angular/common';
import { AuthStateService } from '../../core/auth/auth-state.service';
import { PlayAudioButtonComponent } from '../../shared/play-audio-button/play-audio-button.component';

@Component({
    selector: 'app-definition-guess',
    imports: [
        NgOptimizedImage,
        BottomNavComponent,
        EvaluationBarComponent,
        PlayAudioButtonComponent,
    ],
    templateUrl: './definition-guess.component.html',
    styleUrl: './definition-guess.component.scss',
})
export class DefinitionGuessComponent {
    level = input.required<string>();
    topicId = input.required<string>();
    id = input.required<string>();

    previousPage = output<void>();
    nextPage = output<void>();


    @ViewChild("definitionAudioButton") definitionAudioButton!: PlayAudioButtonComponent;
    @ViewChild("phraseAudioButton") phraseAudioButton!: PlayAudioButtonComponent;
    @ViewChild("sentenceAudioButton") sentenceAudioButton!: PlayAudioButtonComponent;
    @ViewChild("hintAudioButton") hintAudioButton!: PlayAudioButtonComponent;

    private service = inject(DefinitionGuessService);
    private cdr = inject(ChangeDetectorRef);
    public authStateService = inject(AuthStateService);

    public exercise!: DefinitionGuessExercise;
    public sentence!: Sentence;
    public nativeSentence?: NativeSentence;
    public showHint: boolean = false;
    public native: boolean = false;
    public showAnswer: boolean = false;
    public answer: string | null = null;
    public imageSrc!: string;

    constructor() {
        effect(() => {
            const level = this.level();
            const topicId = this.topicId();
            const id = this.id();
            this.service.get(level, topicId, id).subscribe(e => {
                this.answer = null;
                this.exercise = e;
                const sentenceIndex = Math.floor(Math.random() * this.exercise.sentences.length)
                this.sentence = this.exercise.sentences[sentenceIndex];
                this.nativeSentence = this.exercise.native_sentences ? this.exercise.native_sentences[sentenceIndex] : undefined;
                this.showHint = false;
                this.native = false;
                if (this.exercise.image_names) {
                    const imageIndex = Math.floor(Math.random() * this.exercise.image_names.length)
                    this.imageSrc = '/api/images/' + this.exercise.image_names?.[imageIndex];
                } else {
                    this.imageSrc = '';
                }
            })
        });
    }

    onShowHint() {
        this.showHint = true;
        this.cdr.detectChanges();
        this.phraseAudioButton?.pause();
        this.definitionAudioButton?.pause();
        this.hintAudioButton?.play();
    }


    async check(): Promise<void> {
        this.answer = this.sentence.text_with_gap.replace(/_{3,}/g, '<b>' + this.sentence.gap_filler_form + '</b>');
        this.showAnswer = true;
        this.cdr.detectChanges();
        this.definitionAudioButton?.pause();
        this.hintAudioButton?.pause();
        await this.phraseAudioButton?.play();
        this.sentenceAudioButton?.play();
    }

    onEvaluation(evaluation: number): void {
        if (this.authStateService.isAuthenticated()) {
            this.service.evaluate(this.topicId(), this.id(), evaluation).subscribe();
        }
        this.showAnswer = false;
        this.showHint = false;
        this.cdr.detectChanges();
        this.phraseAudioButton?.pause();
        this.definitionAudioButton?.pause();
        this.hintAudioButton?.pause();
        this.nextPage.emit();
    }

}
