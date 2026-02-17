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
    return `/api/target-languages/${targetLanguage}/gap-fill-choices`;
  }

  getAll(): Observable<GapFillChoiceExerciseHeader[]> {
    return this.httpClient.get<GapFillChoiceExerciseHeader[]>(this.getEndpoint());
  }

  get(uid: string): Observable<GapFillChoiceExercise> {
    const nativeLanguage = this.languageService.getInterfaceLanguage();
    return this.httpClient.get<GapFillChoiceExercise>(`${this.getEndpoint()}/${uid}`);
    // return this.httpClient.get<GapFillChoiceExercise>(`${this.getEndpoint()}/${uid}/translations/${nativeLanguage}`);
  }

}
