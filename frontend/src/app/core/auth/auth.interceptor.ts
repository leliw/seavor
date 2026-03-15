import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from './auth.service';
import { catchError, switchMap } from 'rxjs';

const EXCLUDED_ROUTES = [
    '/api/ping',
    '/api/config',
    '/api/login',
    '/api/logout',
    '/api/refresh-token',
    '/api/reset-password-request',
    '/api/reset-password'
];


export const authInterceptor: HttpInterceptorFn = (req, next) => {
    const isExcluded = EXCLUDED_ROUTES.some(route => req.url.endsWith(route));
    if (isExcluded) {
        return next(req);
    }    
    const authService = inject(AuthService);
    const router = inject(Router);
    if (authService.isAuthenticated()) {
        const headers = req.headers.set('Authorization', `Bearer ${authService.access_token}`);
        req = req.clone({ headers });
        return next(req).pipe(
            catchError(err => {
                if (err.status === 401) {
                    return authService.refreshToken().pipe(
                        switchMap(newTokens => {
                            // Retry original request with new token
                            const newReq = req.clone({
                                setHeaders: { Authorization: `Bearer ${newTokens.access_token}` }
                            });
                            return next(newReq);
                        }),
                        catchError(refreshErr => {
                            if (refreshErr.status === 401) {
                                console.error('Refresh token error:', refreshErr);
                                authService.cleanData();
                                router.navigate(['/login']);
                            }
                            throw refreshErr;
                        })
                    );
                };
                throw err;
            }));
    } else {
        router.navigate(['/login']);
        throw new Error('Unauthorized');
    }
};
