import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from "@angular/material/icon";
import { MatToolbarModule } from "@angular/material/toolbar";
import { Router } from '@angular/router';
import { TeacherDefinitionGuessCreate, TeacherServiceService } from '../teacher-service.service';
import { MatInputModule } from "@angular/material/input";
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-teacher-add-page',
  imports: [
    ReactiveFormsModule,
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
    MatInputModule
],
  templateUrl: './teacher-add-page.component.html',
  styleUrl: './teacher-add-page.component.scss',
})
export class TeacherAddPageComponent {
  private router = inject(Router);
  private snackBar = inject(MatSnackBar);
  private service = inject(TeacherServiceService);
  private fb = inject(FormBuilder);

  form = this.fb.group({
    language: ['en'],
    level: ['B1'],
    phrase: ['', Validators.required],
    native_language: ['pl'],
  });

  onClose() {
    this.router.navigate(['/topics']);
  }

  onSubmit(): void {
    if (this.form.invalid) {
      console.warn("Form is invalid");
      return;
    }
    const formData = this.form.value as TeacherDefinitionGuessCreate;
    this.service.post(formData).subscribe({
      next: () => this.snackBar.open($localize`Page created`, $localize`Close`, { duration: 5000 }).afterDismissed().subscribe(() => this.onClose()),
      error: (error) => this.onError('Error creating page:', error),
    });

  }

  onError(message: string, error: Error): void {
    console.error(message, error);
    this.snackBar.open(message, $localize`Close`, { duration: 5000 });
  }

}
