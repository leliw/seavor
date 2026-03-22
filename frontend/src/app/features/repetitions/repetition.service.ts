import { HttpClient } from '@angular/common/http';
import { effect, Injectable, signal, untracked } from '@angular/core';
import { BehaviorSubject, interval, map, Observable } from 'rxjs';

import { parseISO } from 'date-fns';
import { isAfter } from 'date-fns';
import { AuthStateService } from '../../core/auth/auth-state.service';

export interface RepetitionCardHeader {
  id: string;
  language: string;
  level: string;
  topic_id: string;
  page_id: string;
  type: string;
  due: string
}

interface RepetitionSchedule {
  [key: string]: number;
}

@Injectable({
  providedIn: 'root',
})
export class RepetitionService {
  repetitionSchedule: { [key: string]: number } = {};
  
  private numberOfOverdueSubject = new BehaviorSubject<number | null>(null);
  public numberOfOverdue$ = this.numberOfOverdueSubject.asObservable()
  
  firstOverdue = signal<string | undefined>(undefined);

  
  constructor(private httpClient: HttpClient, authStateService: AuthStateService) {
    effect((onCleanup) => {
      if (authStateService.isAuthenticated()) {
        untracked(() => {
          const httpSub = this.getSchedule().subscribe(schedule => {
              this.repetitionSchedule = schedule;
              this.firstOverdue.set(Object.keys(schedule)[0]);
              this.countOverdue();
            });
          const intervalSub = interval(60 * 1000).subscribe(() => {
            this.countOverdue();
          });
          onCleanup(() => {
            httpSub.unsubscribe();
            intervalSub.unsubscribe();
          });
        })
      } else {
        this.repetitionSchedule = {};
        this.numberOfOverdueSubject.next(null);
      }
    });
  }

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

  getSchedule(): Observable<RepetitionSchedule> {
    return this.httpClient.get<RepetitionSchedule>(`${this.getEndpoint()}/schedule`);
  }

  private countOverdue() {
    const now = new Date();
    let numberOfOverdue = 0;
    for (const key in this.repetitionSchedule) {
      if (this.repetitionSchedule.hasOwnProperty(key) && isAfter(now, parseISO(key))) {
        numberOfOverdue += this.repetitionSchedule[key];
      }
    }
    this.numberOfOverdueSubject.next(numberOfOverdue);
  }

}
