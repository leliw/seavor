import { Component, inject } from '@angular/core';
import { FormBuilder, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import {
  MatSnackBar
} from '@angular/material/snack-bar';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../auth.service';
@Component({
  selector: 'app-reset-password-request-form',
  imports: [
    RouterModule,
    ReactiveFormsModule,
    FormsModule,
    MatCardModule,
    MatInputModule,
    MatButtonModule,
    MatFormFieldModule,
  ],
  templateUrl: './reset-password-request-form.component.html',
  styleUrl: './reset-password-request-form.component.scss'
})
export class ResetPasswordRequestFormComponent {

  private fb = inject(FormBuilder);

  form = this.fb.group({
    email: ['', [Validators.email, Validators.required]],
  });

  constructor(
    private router: Router,
    private snackbar: MatSnackBar,
    private authService: AuthService,
  ) { }

  onSubmit() {
    const email = this.form.value.email;
    if (email)
      this.authService.resetPasswordRequest(email).subscribe({
        complete: () => this.snackbar.open($localize`The code was sent to your email: ${email}`, $localize`Reset password`)
          .afterDismissed().subscribe(() =>
            this.router.navigateByUrl("/reset-password")),
        error: (err) => this.snackbar.open($localize`Error: ${err.error.detail}`, $localize`Close`),
      })
  }
}
