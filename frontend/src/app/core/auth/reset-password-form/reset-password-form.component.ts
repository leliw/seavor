import { Component, inject } from '@angular/core';
import { AbstractControl, FormBuilder, ReactiveFormsModule, ValidationErrors, ValidatorFn, Validators } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../auth.service';
import { MatCardModule } from "@angular/material/card";
import { MatInputModule } from "@angular/material/input";
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';

@Component({
  selector: 'app-reset-password-form',
  imports: [
    RouterModule,
    ReactiveFormsModule,
    MatCardModule, 
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
],
  templateUrl: './reset-password-form.component.html',
  styleUrl: './reset-password-form.component.scss'
})
export class ResetPasswordFormComponent {
    private fb = inject(FormBuilder);
    form = this.fb.group({
        email: ['', [Validators.email, Validators.required]],
        reset_code: ['', Validators.required],
        new_password: ['', [Validators.required, passwordStrengthValidator(8)]],
        new_password2: ['', [Validators.required, newPasswordEqualsValidator()]],
    })

    constructor(
        private router: Router,
        private snackbar: MatSnackBar,
        private authService: AuthService,
    ) { }

    onSubmit() {
        const formData = this.form.value;
        if (formData.email && formData.reset_code && formData.new_password)
            this.authService.resetPassword(formData.email, formData.reset_code, formData.new_password).subscribe({
                complete: () => this.snackbar.open($localize`Password changed successfully`, $localize`Login`, { duration: 1500 })
                    .afterDismissed().subscribe(() => this.router.navigateByUrl("/login")),
                error: (err) => this.snackbar.open(err.error.detail ?? err.message, $localize`Close`)
            })
    }
}


export function passwordStrengthValidator(minLength: number): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
        const value: string = control.value;
        if (!value) {
            return null;
        }
        if (value.length < minLength)
            return { minlength: true }
        const hasUpperCase = /[A-Z]+/.test(value);
        const hasLowerCase = /[a-z]+/.test(value);
        const hasNumeric = /[0-9]+/.test(value);
        const passwordValid = hasUpperCase && hasLowerCase && hasNumeric;
        return !passwordValid ? { passwordStrength: true } : null;
    }
}


export function newPasswordEqualsValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
        const value2: string = control.value;
        const value1: string = control.parent?.value.new_password
        return value1 != value2 ? { equals: true } : null;
    }
}
