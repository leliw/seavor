import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { LanguageService } from '../../core/language.service';

export interface GapFillChoiceExerciseHeader {
  id: string;
  level: string;
}

export interface GapFillChoiceExercise {
  id: string;
  level: string;
  target_sentence: string;
  gap_marker: string | null;
  options: string[];
  correct_index: number;
  target_explanation?: string;
  native_explanation?: string;
  target_distractors_explanation?: Record<number, string>;
  native_distractors_explanation?: Record<number, string>;
  target_hint?: string;
  native_hint?: string;
}


@Injectable({
  providedIn: 'root',
})
export class GapFillChoiceService {

  constructor(private httpClient: HttpClient, private languageService: LanguageService) { }

  getEndpoint(): string {
    const targetLanguage = this.languageService.getLearningLanguage();
    const nativeLanguage = this.languageService.getInterfaceLanguage();
    const level = "A1"
    return `/api/native-topics/${targetLanguage}/${level}/${nativeLanguage}`;
  }

  getAll(): Observable<GapFillChoiceExerciseHeader[]> {
    return this.httpClient.get<GapFillChoiceExerciseHeader[]>(this.getEndpoint());
  }

  get(topicId: string, uid: string): Observable<GapFillChoiceExercise> {
    return this.httpClient.get<GapFillChoiceExercise>(`${this.getEndpoint()}/${topicId}/pages/${uid}`);
  }

}
