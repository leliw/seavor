import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable, of, tap } from 'rxjs';
import { UserSettings, DEFAULT_USER_SETTINGS } from './user-settings.model';
import { AuthStateService } from '../auth/auth-state.service';

/**
 * Service responsible for managing user settings.
 * Handles synchronization between the API (if authenticated) and local storage.
 */
@Injectable({
    providedIn: 'root',
})
export class UserSettingsService {
    private http = inject(HttpClient);
    private authStateService = inject(AuthStateService);

    private readonly STORAGE_KEY = 'user_settings';

    /**
     * Retrieves the user settings.
     * If the user is authenticated, it fetches settings from the API and updates local storage.
     * Otherwise, it returns settings from local storage.
     * @returns An observable of the user settings.
     */
    get(): Observable<UserSettings> {
        if (this.authStateService.isAuthenticated()) {
            return this.http.get<UserSettings>('/api/user-settings')
                .pipe(tap(settings => this.saveToLocalStorage(settings)));
        } else {
            return of(this.getFromLocalStorage());
        }
    }

    /**
     * Updates the user settings with the provided partial settings.
     * If the user is authenticated, it sends a patch request to the API and updates local storage.
     * Otherwise, it updates the settings in local storage.
     * @param patch The partial user settings to update.
     * @returns An observable of the updated user settings.
     */
    patch(patch: Partial<UserSettings>): Observable<UserSettings> {
        if (this.authStateService.isAuthenticated()) {
            return this.http.patch<UserSettings>('/api/user-settings', patch)
                .pipe(tap(settings => this.saveToLocalStorage(settings)));
        } else {
            return of(this.updateLocalStorage(patch));
        }
    }

    /**
     * Retrieves user settings from local storage.
     * Returns default settings if local storage is empty or parsing fails.
     * @returns The user settings.
     */
    private getFromLocalStorage(): UserSettings {
        try {
            const json = localStorage.getItem(this.STORAGE_KEY);
            return json ? { ...DEFAULT_USER_SETTINGS, ...JSON.parse(json) } : DEFAULT_USER_SETTINGS;
        } catch (e) {
            console.warn('Failed to parse user settings from localStorage, using defaults', e);
            return DEFAULT_USER_SETTINGS;
        }
    }

    /**
     * Saves the provided user settings to local storage.
     * @param settings The user settings to save.
     */
    private saveToLocalStorage(settings: UserSettings): void {
        try {
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(settings));
        } catch (e) {
            console.error('Failed to save user settings to localStorage', e);
        }
    }

    /**
     * Updates the user settings in local storage with the provided partial settings.
     * @param patch The partial user settings to update.
     * @returns The updated user settings.
     */
    private updateLocalStorage(patch: Partial<UserSettings>): UserSettings {
        const current = this.getFromLocalStorage();
        const updated = { ...current, ...patch } as UserSettings;
        this.saveToLocalStorage(updated);
        return updated;
    }
}
