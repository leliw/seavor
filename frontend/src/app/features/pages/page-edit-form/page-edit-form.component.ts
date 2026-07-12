import { CommonModule, Location } from '@angular/common';
import { Component, computed, inject, input, linkedSignal, signal } from '@angular/core';
import { rxResource } from '@angular/core/rxjs-interop';
import { form, FormField, required } from '@angular/forms/signals';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';
import { finalize } from 'rxjs';
import { getChangedData } from '../../../shared/utils/signal-form.util';
import { PageService } from '../page.service';

@Component({
  selector: 'app-page-edit-form',
  imports: [
    CommonModule,
    FormField,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatProgressSpinnerModule,
    MatButtonModule,
    MatIconModule
  ],
  templateUrl: './page-edit-form.component.html',
  styleUrl: './page-edit-form.component.scss',
})
export class PageEditFormComponent {
  topicId = input.required<string>();
  pageId = input.required<string>();
  service = inject(PageService);

  resource = rxResource({
    params: () => ({ topicId: this.topicId(), pageId: this.pageId() }),
    stream: ({ params }) => this.service.get(params.topicId, params.pageId)
  });
  originalModel = linkedSignal(() => structuredClone(this.resource.value() ?? this.service.new()));
  model = linkedSignal(() => structuredClone(this.originalModel()));
  form = form(this.model, (s) => {
    required(s.phrase, { message: 'Phrase is required' });
    required(s.definition, { message: 'Definition is required' });
  });

  location = inject(Location);
  snackBar = inject(MatSnackBar);

  isLoading = linkedSignal(() => this.resource.isLoading());
  isSaving = signal(false);
  isBusy = computed(() => this.isLoading() || this.isSaving());
  canSubmit = computed(() =>
    !this.isLoading() &&
    !this.isSaving() &&
    this.form().dirty() &&
    !this.form().invalid()
  );

  submit(event: Event) {
    event.preventDefault();
    let changes = getChangedData(this.originalModel(), this.model());
    changes.type = this.originalModel().type;
    this.isSaving.set(true);
    this.service.patch(this.topicId(), this.pageId(), changes).pipe(
      finalize(() => this.isSaving.set(false))
    ).subscribe({
      next: () => {
        this.snackBar.open('Updated successfully!', 'Close', { duration: 3000 });
        this.location.back();
      },
      error: error => {
        this.snackBar.open('Error updating.', 'Close', { duration: 3000 });
        console.error('Error updating:', error);
      }
    });
  }

  cancel(): void {
    this.location.back();
  }

  addSentence() {
    this.model.update(m => ({ ...m, sentences: [...m.sentences, { text_with_gap: '', gap_filler_form: m.phrase }] }));
  }
  removeSentence(index: number) {
    this.model.update(m => ({ ...m, sentences: m.sentences.filter((_, i) => i !== index) }));
  }

  addAlternative() {
    this.model.update(m => ({ ...m, alternatives: [...m.alternatives, { value: "" }] }));
  }
  removeAlternative(index: number) {
    this.model.update(m => ({ ...m, alternatives: m.alternatives.filter((_, i) => i !== index) }));
  }

  addDistractor() {
    this.model.update(m => ({ ...m, distractors: [...m.distractors, { value: "" }] }));
  }
  removeDistractor(index: number) {
    this.model.update(m => ({ ...m, distractors: m.distractors.filter((_, i) => i !== index) }));
  }
}
