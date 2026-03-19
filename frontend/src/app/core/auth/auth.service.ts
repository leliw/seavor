import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { BehaviorSubject, catchError, filter, finalize, Observable, of, take, tap, throwError } from 'rxjs';
import { AuthStateService } from './auth-state.service';


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
    access_token?: string;
    refresh_token?: string;
    store_token = false;
    redirectUrl: string | undefined;
    continueWithoutLogin = false;

    constructor(private http: HttpClient, private router: Router, private authState: AuthStateService) {
        this.loadTokensFromLocalStorage();
    }

    private loadTokensFromLocalStorage(): void {
        const storedAccessToken = localStorage.getItem("access_token");
        const storedRefreshToken = localStorage.getItem("refresh_token");

        if (storedAccessToken && storedRefreshToken) {
            this.access_token = storedAccessToken;
            this.refresh_token = storedRefreshToken;
            this.store_token = true; // Assume if tokens were stored, we want to continue storing them
            this.authState.setUserData({ access_token: storedAccessToken, refresh_token: storedRefreshToken });
            this.continueWithoutLogin = false;
        }
    }

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
            tap((tokens) => {
                this.authState.setUserData(tokens);
                this.continueWithoutLogin = false;
                this.storeTokensIfNeeded(tokens);
                this.redirectAfterLogin();
            })
        );
    }

    /**
     * Logout user from server, clear data and redirect to login page
     * @returns Observable<void>
     */
    logout(): Observable<void> {
        if (this.refresh_token) {
            const headers = new HttpHeaders({ 'Authorization': `Bearer ${this.refresh_token}` });
            return this.http.post<void>('/api/logout', {}, { headers: headers }).pipe(finalize(() => {
                this.authState.clear();
                this.clearStoredTokens();
                this.router.navigate(['/login']);
            }));
        } else {
            this.authState.clear();
            this.clearStoredTokens();
            this.router.navigate(['/login']);
            return of(undefined);
        }
    }

    redirectAfterLogin(): void {
        if (this.redirectUrl) {
            this.router.navigate([this.redirectUrl]);
            this.redirectUrl = undefined;
        } else {
            this.router.navigate(['/']);
        }
    }

    /**
     * Check if user is logged in
     * @returns boolean
     */
    isAuthenticated(): boolean {
        return this.authState.isAuthenticated();
    }

    /**
     * Set tokens (also in browser local storage)
     * @param tokens 
     */
    storeTokensIfNeeded(tokens: Tokens): void {
        this.access_token = tokens.access_token;
        this.refresh_token = tokens.refresh_token
        if (this.store_token) {
            localStorage.setItem("access_token", this.access_token);
            localStorage.setItem("refresh_token", this.refresh_token);
        }
    }

    clearStoredTokens(): void {
        this.access_token = undefined;
        this.refresh_token = undefined;
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
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
                this.authState.setUserData(tokens);
                this.storeTokensIfNeeded(tokens);
                this.refreshTokenSubject.next(tokens);
            }),
            catchError(err => {
                this.authState.clear();
                this.clearStoredTokens()
                this.router.navigate(['/login']);
                return throwError(() => err);
            }),
            finalize(() => {
                this.isRefreshing = false;
            })
        );
    }
}
