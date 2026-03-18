import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable, of, tap } from 'rxjs';
import { UserSettings } from './user-settings.model';
import { AuthStateService } from '../auth/auth-state.service';

@Injectable({
    providedIn: 'root',
})
export class UserSettingsService {
    private readonly STORAGE_KEY = 'user_settings';

    constructor(private http: HttpClient, private authStateService: AuthStateService) { }

    get(): Observable<UserSettings> {
        if (this.authStateService.isAuthenticated())
            return this.http.get<UserSettings>('/api/user-settings')
                .pipe(tap(settings => this.saveToLocalStorage(settings)));
        else
            return of(this.getFromLocalStorage())

    }

    patch(patch: Partial<UserSettings>): Observable<UserSettings> {
        if (this.authStateService.isAuthenticated())
            return this.http.patch<UserSettings>('/api/user-settings', patch)
                .pipe(tap(settings => this.saveToLocalStorage(settings)));
        else {
            return of(this.updateLocalStorage(patch));
        }
    }

    private getFromLocalStorage(): UserSettings {
        try {
            const json = localStorage.getItem(this.STORAGE_KEY);
            return json ? JSON.parse(json) : {} as UserSettings;
        } catch (e) {
            console.warn('Failed to parse user settings from localStorage', e);
            return {} as UserSettings;
        }
    }

    private saveToLocalStorage(settings: UserSettings): void {
        try {
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(settings));
        } catch (e) {
            console.error('Failed to save user settings to localStorage', e);
        }
    }

    private updateLocalStorage(patch: Partial<UserSettings>): UserSettings {
        const current = this.getFromLocalStorage();
        const updated = { ...current, ...patch } as UserSettings
        this.saveToLocalStorage(updated);
        return updated
    }

}
