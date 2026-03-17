import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from './auth.service';
import { MatSnackBar } from '@angular/material/snack-bar';

export const authGuard: CanActivateFn = (route, state) => {
    const authService = inject(AuthService);
    const router = inject(Router);
    const snackBar = inject(MatSnackBar);

    if (!authService.isAuthenticated()) {
        authService.redirectUrl = state.url
        router.navigate(['/login']);
        return false;
    } else if (route.data['roles'] && !authService.hasAnyRole(route.data['roles'])) {
        snackBar.open($localize`Permission denied`, $localize`Close`);
        router.navigate(['/']);
        return false;
    } else
        return true;
};
