import { Component } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../auth.service';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { MatButton } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Observable } from 'rxjs';
import { ConfigService } from '../../config.service';

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
export class LoginFormComponent {
    credentials = { username: '', password: '' };
    store_token = false;

    version$: Observable<string>;

    constructor(private configService: ConfigService, private authService: AuthService, private router: Router, private snackBar: MatSnackBar) {
        this.version$ = this.configService.getConfigValue$("version");
        if (authService.isAuthenticated())
            this.router.navigate(['/']);
    }

    onSubmit() {
        this.authService.login(this.credentials, this.store_token).subscribe({
            error: (err) => {
                if (err.status == 401)
                    this.snackBar.open($localize`Wrong username or password`, $localize`Close`, { duration: 1500 });
                else {
                    console.warn(err.message);
                    this.snackBar.open(err.message, $localize`Close`);
                }
            }
        });
    }

    continueWithoutAccount() {
        this.authService.continueWithoutLogin = true;
        this.router.navigate(['/']);
    }
}
