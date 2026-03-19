import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from './auth.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { AuthStateService } from './auth-state.service';

export const authGuard: CanActivateFn = (route, state) => {
    const authStateService = inject(AuthStateService);
    const router = inject(Router);
    const snackBar = inject(MatSnackBar);

    if (!authStateService.isAuthenticated()) {
        const authService = inject(AuthService);
        authService.redirectUrl = state.url
        router.navigate(['/login']);
        return false;
    } else if (route.data['roles'] && !authStateService.hasAnyRole(route.data['roles'])()) {
        snackBar.open($localize`Permission denied`, $localize`Close`);
        router.navigate(['/']);
        return false;
    } else
        return true;
};
