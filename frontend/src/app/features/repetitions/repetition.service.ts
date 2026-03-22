import { HttpClient } from '@angular/common/http';
import { effect, Injectable, signal, untracked } from '@angular/core';
import { BehaviorSubject, catchError, combineLatest, interval, map, Observable, of, tap } from 'rxjs'; // Dodaj combineLatest

import { isAfter, parseISO } from 'date-fns';
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
  private repetitionScheduleSubject = new BehaviorSubject<RepetitionSchedule | null>(null);

  public repetitionSchedule$ = this.repetitionScheduleSubject.asObservable();
  public numberOfOverdue$ = combineLatest([
    this.repetitionSchedule$,
    interval(60 * 1000)
  ]).pipe(
    map(([schedule, _]) => {
      if (!schedule) return null;
      else {
        const now = new Date();
        let numberOfOverdue = 0;
        for (const key in schedule) {
          if (schedule.hasOwnProperty(key) && isAfter(now, parseISO(key))) {
            numberOfOverdue += schedule[key];
          }
        }
        return numberOfOverdue;
      }
    })
  );

  earliestOverdue = signal<string | undefined>(undefined);


  constructor(private httpClient: HttpClient, authStateService: AuthStateService) {
    effect((onCleanup) => {
      if (authStateService.isAuthenticated()) {
        untracked(() => {
          const httpSub = this.getSchedule().subscribe();
          onCleanup(() => httpSub.unsubscribe());
        })
      } else {
        this.repetitionScheduleSubject.next(null);
        this.earliestOverdue.set(undefined);
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
    return this.httpClient.get<RepetitionSchedule>(`${this.getEndpoint()}/schedule`)
      .pipe(
        tap(schedule => {
          this.repetitionScheduleSubject.next(schedule);
          this.earliestOverdue.set(
            Object.keys(schedule).sort((a, b) => parseISO(a).getTime() - parseISO(b).getTime())[0]
          );
        }),
        catchError(error => {
          console.error('Error fetching repetition schedule: ', error);
          this.repetitionScheduleSubject.next({});
          this.earliestOverdue.set(undefined);
          return of({});
        })
      );
  }
}
