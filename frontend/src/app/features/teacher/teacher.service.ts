import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { BaseTask } from '../../shared/task.service';

export interface TeacherDefinitionGuessCreate {
  language: string;
  level?: string;
  phrase: string;
  native_language?: string;
}

@Injectable({
  providedIn: 'root',
})
export class TeacherService {
  private readonly http = inject(HttpClient);
  private readonly endpoint = '/api/teacher/definition-guess';

  post(body: TeacherDefinitionGuessCreate): Observable<BaseTask> {
    return this.http.post<BaseTask>(this.endpoint, body);
  }

}
