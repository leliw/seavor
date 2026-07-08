import { Component, inject, ChangeDetectionStrategy } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from "@angular/material/icon";
import { MatInputModule } from "@angular/material/input";
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatToolbarModule } from "@angular/material/toolbar";
import { Router } from '@angular/router';
import { RepetitionService } from '../../repetitions/repetition.service';
import { TeacherDefinitionGuessCreate, TeacherService } from '../teacher.service';

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
  changeDetection: ChangeDetectionStrategy.Eager,
  styleUrl: './teacher-add-page.component.scss',
})
export class TeacherAddPageComponent {
  private router = inject(Router);
  private snackBar = inject(MatSnackBar);
  private service = inject(TeacherService);
  private fb = inject(FormBuilder);

  private repetitionService = inject(RepetitionService);

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
      next: (task) => {
        this.snackBar.open($localize`Creating exercise in background...`, $localize`OK`, { duration: 3000 });
        this.repetitionService.pollCreatingTaskStatus(task.id);
        this.onClose();
      },
      error: (error) => this.onError('Error creating page:', error),
    });

  }

  onError(message: string, error: Error): void {
    console.error(message, error);
    this.snackBar.open(message, $localize`Close`, { duration: 5000 });
  }

}
