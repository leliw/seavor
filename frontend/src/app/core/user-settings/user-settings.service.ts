import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { UserSettings } from './user-settings.model';

@Injectable({
    providedIn: 'root',
})
export class UserSettingsService {
    constructor(private http: HttpClient) { }

    get(): Observable<UserSettings> {
        return this.http.get<UserSettings>('/api/user-settings');
    }

    patch(patch: Partial<UserSettings>): Observable<UserSettings> {
        return this.http.patch<UserSettings>('/api/user-settings', patch);
    }
}
