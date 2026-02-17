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
  sentence: string;
  gapMarker: string | null;
  options: string[];
  correctIndex: number;
  target_explanation?: string;
  native_explanation?: string;
  target_distractorsExplanation?: Record<number, string>;
  native_distractorsExplanation?: Record<number, string>;
  audioUrl?: string;              // nagranie całego zdania (do ćwiczeń listening + gap-fill)
  hint?: string;                  // podpowiedź po pierwszym niepowodzeniu
  tags?: string[];                // np. ["semi-modals", "advice", "obligation"]
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
    // return this.httpClient.get<GapFillChoiceExercise>(`${this.getEndpoint()}/${uid}/translations/${nativeLanguage}`);
    return of({
      id: uid,
      level: "B1",
      sentence: "You _____ see a doctor – that cough sounds bad!",
      gapMarker: "_____",
      options: ["ought to", "used to", "had better", "need"],
      correctIndex: 2,
      target_explanation: "had better – strong advice / warning in the present situation",
      native_explanation: "had better – silna rada / ostrzeżenie w obecnej sytuacji",
      target_distractorsExplanation: {
        0: "ought to – za słabe, to tylko łagodna sugestia",
        1: "used to – dotyczy przeszłych nawyków, nie pasuje",
        3: "need – oznacza konieczność, a nie radę"
      },
    } as GapFillChoiceExercise)
  }

}
