import { Component, inject, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { AuthService } from '../auth.service';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { MatButton } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatSnackBar } from '@angular/material/snack-bar';
import { filter, map, Observable, of, switchMap, take } from 'rxjs';
import { ConfigService } from '../../config.service';
import { FullscreenLoaderService } from '../../../shared/fullscreen-loader.service';

@Component({
    selector: 'app-login-form',
    imports: [
        CommonModule,
        FormsModule,
        MatCardModule,
        MatInputModule,
        MatButton,
        MatFormFieldModule,
        MatCheckboxModule,
        RouterModule,
    ],
    templateUrl: './login-form.component.html',
    styleUrl: './login-form.component.scss'
})
export class LoginFormComponent implements OnInit, OnDestroy {
    credentials = { username: '', password: '' };
    store_token = false;
    version$: Observable<string> = of("");

    private configService = inject(ConfigService);
    private authService = inject(AuthService);
    private router = inject(Router);
    private snackBar = inject(MatSnackBar);
    private activatedRoute = inject(ActivatedRoute);
    private loader = inject(FullscreenLoaderService);

    constructor() {
        if (this.authService.isAuthenticated())
            this.router.navigate(['/']);
        this.store_token = JSON.parse(sessionStorage.getItem('remember_me') ?? 'false');
    }

    ngOnInit(): void {
        this.version$ = this.configService.getConfigValue$("version");
        this.activatedRoute.queryParams.pipe(
            map(params => params['exchange-code']),
            filter(code => !!code),
            take(1),
            switchMap(code => {
                this.loader.show({ message: 'Signing in ...' });
                const rememberMe = JSON.parse(sessionStorage.getItem('remember_me') || 'false');
                return this.authService.loginWithExchangeCode(code, rememberMe);
            })
        ).subscribe({
            error: (err) => {
                this.loader.hide();
                if (err.status === 401)
                    this.snackBar.open('Authentication failed', 'Close', { duration: 1500 });
                else {
                    console.warn(err.message);
                    this.snackBar.open(err.message, 'Close');
                }
            }
        });
    }

    ngOnDestroy(): void {
        if (this.loader.isVisible())
            this.loader.hide();
    }

    onSubmit() {
        this.loader.show({ message: 'Signing in ...' });
        this.authService.login(this.credentials, this.store_token).subscribe({
            error: (err) => {
                this.loader.hide();
                if (err.status === 401)
                    this.snackBar.open($localize`Wrong username or password`, $localize`Close`, { duration: 1500 });
                else {
                    console.warn(err.message);
                    this.snackBar.open(err.message, $localize`Close`);
                }
            }
        });
    }

    loginWithGoogle() {
        sessionStorage.setItem('remember_me', JSON.stringify(this.store_token));
        const baseUrl = window.location.origin;
        window.location.href = `/api/google/login?base_url=` + encodeURIComponent(baseUrl);;
    }

    continueWithoutAccount() {
        this.authService.continueWithoutLogin = true;
        this.router.navigate(['/']);
    }
}
