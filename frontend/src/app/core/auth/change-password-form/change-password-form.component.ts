import { Component, inject, OnInit, ChangeDetectionStrategy } from '@angular/core';
import { AbstractControl, FormBuilder, ReactiveFormsModule, ValidationErrors, ValidatorFn, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { AuthService } from '../auth.service';
import { passwordStrengthValidator, newPasswordEqualsValidator } from '../../validators';
import { User, UserService } from '../../users/user.service';

@Component({
    selector: 'app-change-password-form',
    imports: [
        RouterModule,
        ReactiveFormsModule,
        MatCardModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
    ],
    templateUrl: './change-password-form.component.html',
    changeDetection: ChangeDetectionStrategy.Eager,
    styleUrl: './change-password-form.component.scss'
})
export class ChangePasswordFormComponent implements OnInit {
    private fb = inject(FormBuilder);
    form = this.fb.group({
        old_password: ['', Validators.required],
        new_password: ['', [Validators.required, Validators.minLength(8), passwordStrengthValidator(8)]],
        new_password2: ['', [Validators.required, newPasswordEqualsValidator()]],
    })

    username: string | null = null;

    constructor(
        private router: Router,
        private route: ActivatedRoute,
        private snackbar: MatSnackBar,
        private authService: AuthService,
        private userService: UserService
    ) { }

    ngOnInit(): void {
        this.username = this.route.snapshot.paramMap.get('username');
        if (this.username) {
            this.form.controls['old_password'].setValidators([]);
            this.form.controls['old_password'].updateValueAndValidity();
        }
    }

    onSubmit() {
        const formData = this.form.value;
        if (this.username) {
            if (formData.new_password)
                this.userService.changePassword(this.username, formData.new_password).subscribe({
                    complete: () => this.snackbar.open('Password changed successfully.', 'Close', { duration: 1500 })
                        .afterDismissed().subscribe(() => this.router.navigateByUrl("/users")),
                    error: (err) => this.snackbar.open(err.error.detail ?? err.message, 'Close')
                })

        } else {
            if (formData.old_password && formData.new_password)
                this.authService.changePassword(formData.old_password, formData.new_password).subscribe({
                    complete: () => this.snackbar.open('Password changed successfully.', 'Close', { duration: 1500 })
                        .afterDismissed().subscribe(() => this.router.navigateByUrl("/")),
                    error: (err) => this.snackbar.open(err.error.detail ?? err.message, 'Close')
                })
        }
    }
}
