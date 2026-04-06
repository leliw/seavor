import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { RepetitionCardHeader } from '../repetitions/repetition.service';

export interface TeacherDefinitionGuessCreate {
  language: string;
  level?: string;
  phrase: string;
  native_language?: string;
}

@Injectable({
  providedIn: 'root',
})
export class TeacherServiceService {
  private readonly http = inject(HttpClient);
  private readonly endpoint = '/api/teacher/definition-guess';

  post(body: TeacherDefinitionGuessCreate): Observable<RepetitionCardHeader> {
    return this.http.post<RepetitionCardHeader>(this.endpoint, body);
  }

}
