import { Component, effect, inject, input, OnDestroy, output } from '@angular/core';
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
export class DefinitionGuessComponent implements OnDestroy {
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

    phrase_audio: HTMLAudioElement = new Audio();
    definition_audio: HTMLAudioElement = new Audio();
    hint_audio: HTMLAudioElement = new Audio();
    sentence_audio: HTMLAudioElement = new Audio();

    constructor() {
        effect(() => {
            const topicId = this.topicId();
            const id = this.id();
            this.service.get(topicId, id).subscribe(e => {
                this.answer = null;
                this.exercise = e;
                const sentenceIndex = Math.floor(Math.random() * this.exercise.sentences.length)
                this.sentence = this.exercise.sentences[sentenceIndex];
                this.sentence_audio.src = '/api/audio-files/' + this.sentence.audio_file_name;
                this.sentence_audio.load();
                this.nativeSentence = this.exercise.native_sentences ? this.exercise.native_sentences[sentenceIndex] : undefined;
                this.showHint = false;
                this.native = false;
                this.definition_audio.src = '/api/audio-files/' + this.exercise.definition_audio_file_name;
                this.definition_audio.load();
                this.definition_audio.play().catch(err => console.error('Audio play error:', err));
                this.hint_audio.src = '/api/audio-files/' + this.exercise.hint_audio_file_name;
                this.hint_audio.load();
                setTimeout(() => {
                    this.phrase_audio.src = '/api/audio-files/' + this.exercise.phrase_audio_file_name;
                    this.phrase_audio.load();
                }, 500);
            })
        });
    }

    onShowHint() {
        this.showHint = true;
        this.definition_audio.pause();
        this.hint_audio.play().catch(err => console.error('Audio play error:', err));
    }
    check(): void {
        this.answer = this.sentence.text_with_gap.replace(/_{3,}/g, '<b>' + this.sentence.gap_filler_form + '</b>');
        this.showAnswer = true;
        this.definition_audio.pause();
        this.hint_audio.pause();
        this.phrase_audio.addEventListener('ended', () => {
                this.sentence_audio.play().catch(err => console.error('Audio play error:', err));
            }, { once: true });
        this.phrase_audio.play().catch(err => console.error('Audio play error:', err));
        
    }

    onEvaluation(evaluation: number): void {
        console.log(evaluation);
        this.showAnswer = false;
        this.showHint = false;
        this.phrase_audio.pause();
        this.sentence_audio.pause();
        this.nextPage.emit();
    }

    ngOnDestroy(): void {
        this.phrase_audio.pause();
        this.phrase_audio.src = '';
        this.definition_audio.pause();
        this.definition_audio.src = '';
        this.hint_audio.pause();
        this.hint_audio.src = '';
        this.sentence_audio.pause();
        this.sentence_audio.src = '';
    }
}
