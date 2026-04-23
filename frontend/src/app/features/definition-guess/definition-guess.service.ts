import { HttpClient } from '@angular/common/http';
import { computed, inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { UserSettingsStore } from '../../core/user-settings/user-settings.store';

export interface Sentence {
    text_with_gap: string;
    gap_filler_form: string;
    audio_file_name?: string;
}

export interface NativeSentence {
    text: string;
    audio_file_name?: string;
}

export interface AnswerOption {
    value: string;
    explanation?: string;
    audio_file_name?: string;
}

export interface DefinitionGuessExercise {
    id: string;
    language: string;
    level: string;

    phrase: string;
    definition: string;
    sentences: Sentence[];

    alternatives: AnswerOption[];
    distractors: AnswerOption[];

    hint?: string;
    explanation?: string;

    phrase_audio_file_name?: string;
    definition_audio_file_name?: string;
    hint_audio_file_name?: string;
    explanation_audio_file_name?: string;

    native_definition?: string;
    native_hint?: string;
    native_explanation?: string;
    native_sentences?: NativeSentence[];

    image_names?: string[];
}

@Injectable({
    providedIn: 'root',
})
export class DefinitionGuessService {
    private userSettingsStorage = inject(UserSettingsStore);
    private language = computed(() => this.userSettingsStorage.settings().learning_language);
    private level = computed(() => this.userSettingsStorage.settings().learning_level);
    private uiLanguage = computed(() => this.userSettingsStorage.settings().ui_language);

    constructor(private httpClient: HttpClient) { }

    getEndpoint(level: string | undefined = undefined): string {
        return `/api/topics/${this.language()}/${level ?? this.level()}`;
    }

    getNativeEndpoint(level: string | undefined): string {
        return `/api/native-topics/${this.language()}/${level ?? this.level()}/${this.uiLanguage()}`;
    }

    get(level: string, topicId: string, pageId: string): Observable<DefinitionGuessExercise> {
        return this.httpClient.get<DefinitionGuessExercise>(`${this.getNativeEndpoint(level)}/${topicId}/pages/${pageId}`);
    }

    addImage(level: string, topicId: string, pageId: string): Observable<void> {
        return this.httpClient.post<void>(`${this.getEndpoint(level)}/${topicId}/pages/${pageId}/generate-image`, {});
    }

    evaluate(topicId: string, pageId: string, rate: number): Observable<void> {
        return this.httpClient.post<void>(`${this.getEndpoint()}/${topicId}/pages/${pageId}/evaluate`, { rating: rate });
    }
}
