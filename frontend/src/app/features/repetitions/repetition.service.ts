import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';
import { LanguageService } from '../../core/language.service';

import { parseISO } from 'date-fns';
import { isAfter } from 'date-fns';

export interface RepetitionCardHeader {
  id: string;
  language: string;
  level: string;
  topic_id: string;
  page_id: string;
  type: string;
  due: string
}


@Injectable({
  providedIn: 'root',
})
export class RepetitionService {
  constructor(private httpClient: HttpClient, private languageService: LanguageService) { }

  getEndpoint(): string {
    return `/api/repetitions`;
  }

  getAll(): Observable<RepetitionCardHeader[]> {
    return this.httpClient.get<RepetitionCardHeader[]>(this.getEndpoint());
  }

  getOverdue(): Observable<RepetitionCardHeader[]> {
    return this.getAll().pipe(map(reps => reps.filter(rep => this.isOverdue(rep.due))));
  }


  private isOverdue(due: string): boolean {
    if (!due) return false;

    const dueDate = parseISO(due);
    const now = new Date();

    return isAfter(now, dueDate);
  }
}
