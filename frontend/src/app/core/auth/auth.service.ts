import { HttpClient, HttpHeaders } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { jwtDecode } from 'jwt-decode';
import { BehaviorSubject, catchError, filter, finalize, Observable, take, tap, throwError } from 'rxjs';
import { UserSettingsStore } from '../user-settings/user-settings.store';


export interface Credentials {
    username: string;
    password: string;
}

export interface Tokens {
    access_token: string;
    refresh_token: string;
}

@Injectable({
    providedIn: 'root'
})
export class AuthService {
    username?: string;
    access_token?: string;
    refresh_token?: string;
    user_email?: string;
    roles: string[] = [];
    user_photo_url?: string;
    store_token = false;
    redirectUrl: string | undefined;
    continueWithoutLogin = false;

    private userSettingsStore = inject(UserSettingsStore);

    constructor(private http: HttpClient, private router: Router) { }

    /**
     * Login user with username and password
     * @param credentials 
     * @returns 
     */
    login(credentials: Credentials, store_token = false): Observable<Tokens> {
        const formData = new FormData();
        formData.append('username', credentials.username);
        formData.append('password', credentials.password);
        this.store_token = store_token;
        return this.http.post<Tokens>('/api/login', formData).pipe(
            tap((value) => {
                this.setData(value);
                this.continueWithoutLogin = false;
                this.userSettingsStore.load();
            })
        );
    }

    /**
     * Logout user from server, clear data and redirect to login page
     * @returns Observable<void>
     */
    logout(): Observable<void> {
        const headers = new HttpHeaders({ 'Authorization': `Bearer ${this.refresh_token}` });
        return this.http.post<void>('/api/logout', {}, { headers: headers }).pipe(finalize(() => {
            this.cleanData();
            this.router.navigate(['/login']);
        }));
    }

    /**
     * Set tokens, user data decoded from token and
     * redirects if necessary
     * @param tokens 
     */
    setData(tokens: Tokens): void {
        this.setTokens(tokens);
        this.decodeToken(tokens.access_token);
        if (this.redirectUrl) {
            this.router.navigate([this.redirectUrl]);
            this.redirectUrl = undefined;
        } else {
            this.router.navigate(['/']); // Przekierowanie na stronę główną
        }
    }

    /**
     * Clear user data and remove tokens from local storage
     */
    cleanData(): void {
        this.access_token = undefined;
        this.username = undefined;
        this.user_email = undefined;
        this.roles = [];
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
    }

    /**
     * Check if user is logged in
     * @returns boolean
     */
    isAuthenticated(): boolean {
        if (this.username)
            return true;
        this.access_token = localStorage.getItem("access_token") ?? undefined
        this.refresh_token = localStorage.getItem("refresh_token") ?? undefined
        if (this.refresh_token) {
            this.decodeToken(this.refresh_token);
            return true;
        }
        return false;
    }

    hasRole(role: string): boolean {
        return this.roles.includes(role);
    }

    hasAnyRole(requiredRoles: string[]): boolean {
        return requiredRoles.some(role => this.roles.includes(role));
    }

    hasAllRoles(requiredRoles: string[]): boolean {
        return requiredRoles.every(role => this.roles.includes(role));
    }
    
    /**
     * Decode JWT token and set user data
     * @param token JWT token
     */
    private decodeToken(token: string): void {
        const payload: any = jwtDecode(token);
        this.username = payload.sub;
        this.user_email = payload.email;
        this.roles = payload.roles;
        this.user_photo_url = payload.picture;
    }

    /**
     * Set tokens (also in browser local storage)
     * @param tokens 
     */
    setTokens(tokens: Tokens): void {
        this.access_token = tokens.access_token;
        this.refresh_token = tokens.refresh_token
        if (this.store_token) {
            localStorage.setItem("access_token", this.access_token);
            localStorage.setItem("refresh_token", this.refresh_token);
        }
    }

    resetPasswordRequest(email: string): Observable<void> {
        return this.http.post<void>("/api/reset-password-request", { email: email });
    }

    resetPassword(email: string, reset_code: string, new_password: string): Observable<void> {
        return this.http.post<void>("/api/reset-password", {
            email: email,
            reset_code: reset_code,
            new_password: new_password
        });
    }

    changePassword(old_password: string, new_password: string): Observable<void> {
        return this.http.post<void>('/api/change-password', {
            old_password: old_password,
            new_password: new_password
        });
    }
    private isRefreshing = false;
    private refreshTokenSubject: BehaviorSubject<Tokens | null> = new BehaviorSubject<Tokens | null>(null);

    refreshToken(): Observable<Tokens> {
        if (this.isRefreshing) {
            // If already refreshing, wait for new access token
            return this.refreshTokenSubject.pipe(
                filter(token => token !== null),
                take(1)
            );
        }

        this.isRefreshing = true;
        this.refreshTokenSubject.next(null);

        const headers = new HttpHeaders({
            'Authorization': `Bearer ${this.refresh_token}`
        });

        return this.http.post<Tokens>('/api/refresh-token', {}, { headers }).pipe(
            tap(tokens => {
                this.setTokens(tokens);
                this.decodeToken(tokens.access_token);
                this.refreshTokenSubject.next(tokens);
            }),
            catchError(err => {
                this.cleanData();
                this.router.navigate(['/login']);
                return throwError(() => err);
            }),
            finalize(() => {
                this.isRefreshing = false;
            })
        );
    }
}
