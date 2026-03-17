import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { LanguageService } from '../../core/language.service';
import { Observable, of } from 'rxjs';

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
    constructor(private httpClient: HttpClient, private languageService: LanguageService) { }

    getEndpoint(): string {
        const language = this.languageService.getLearningLanguage();
        const level = "B1"
        return `/api/topics/${language}/${level}`;
    }

    getNativeEndpoint(): string {
        const language = this.languageService.getLearningLanguage();
        const nativeLanguage = this.languageService.getInterfaceLanguage();
        const level = "B1"
        return `/api/native-topics/${language}/${level}/${nativeLanguage}`;
    }

    get(topicId: string, uid: string): Observable<DefinitionGuessExercise> {
        return this.httpClient.get<DefinitionGuessExercise>(`${this.getNativeEndpoint()}/${topicId}/pages/${uid}`);
    }

    evaluate(topicId: string, uid: string, rate: number): Observable<void> {
        return this.httpClient.post<void>(`${this.getEndpoint()}/${topicId}/pages/${uid}/evaluate`, { rating: rate });
    }
}
