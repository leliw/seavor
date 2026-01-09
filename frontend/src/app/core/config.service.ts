import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, catchError, filter, map, Observable, of, shareReplay, tap } from 'rxjs';

export interface Config {
    version: string;
}

@Injectable({
    providedIn: 'root'
})
export class ConfigService {
    private readonly url = '/api/config';
    private configSubject = new BehaviorSubject<Config | null>(null);
    public config$ = this.configSubject.asObservable().pipe(filter((c): c is Config => !!c));
    private loadConfig$?: Observable<Config>;

    constructor(private http: HttpClient) { }

    public loadConfig(): Observable<Config> {
        if (this.configSubject.value) {
            return of(this.configSubject.value);
        }
        if (!this.loadConfig$) {
            this.loadConfig$ = this.http.get<Config>(this.url).pipe(
                tap(config => this.configSubject.next(config)),
                shareReplay(1),
                catchError(err => {
                    console.error('Failed to load config', err);
                    const fallbackConfig = { version: 'unknown' };
                    this.configSubject.next(fallbackConfig);
                    return of(fallbackConfig);
                })
            );
        }
        return this.loadConfig$;
    }

    getConfigValue<K extends keyof Config>(key: K): Config[K] | null {
        return this.configSubject.value ? this.configSubject.value[key] : null;
    }

    getConfigValue$<K extends keyof Config>(key: K): Observable<Config[K]> {
        return this.config$.pipe(map(config => config[key]));
    }
}