import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { LanguageService } from '../../core/language.service';

export interface GapFillChoiceExerciseHeader {
    id: string;
    level: string;
}

export interface GapFillChoiceExercise {
    id: string;
    level: string;
    sentence: string;
    gap_marker: string | null;
    options: string[];
    correct_index: number;
    explanation?: string;
    native_explanation?: string;
    distractors_explanation?: Record<number, string>;
    native_distractors_explanation?: Record<number, string>;
    hint?: string;
    native_hint?: string;
}


@Injectable({
    providedIn: 'root',
})
export class GapFillChoiceService {

    constructor(private httpClient: HttpClient, private languageService: LanguageService) { }

    getEndpoint(): string {
        const nativeLanguage = this.languageService.getInterfaceLanguage();
        return `/api/native-topics/${nativeLanguage}`;
    }

    getAll(): Observable<GapFillChoiceExerciseHeader[]> {
        return this.httpClient.get<GapFillChoiceExerciseHeader[]>(this.getEndpoint());
    }

    get(topicId: string, uid: string): Observable<GapFillChoiceExercise> {
        return this.httpClient.get<GapFillChoiceExercise>(`${this.getEndpoint()}/${topicId}/pages/${uid}`);
    }

}
