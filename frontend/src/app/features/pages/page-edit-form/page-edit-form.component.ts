import { CommonModule, Location, NgOptimizedImage } from '@angular/common';
import { Component, computed, inject, input, linkedSignal, signal } from '@angular/core';
import { rxResource } from '@angular/core/rxjs-interop';
import { form, FormField, required } from '@angular/forms/signals';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from "@angular/material/card";
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatTabsModule } from '@angular/material/tabs';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatTooltip } from "@angular/material/tooltip";
import { finalize } from 'rxjs';
import { FullscreenLoaderService } from '../../../shared/fullscreen-loader.service';
import { getChangedData } from '../../../shared/utils/signal-form.util';
import { DefinitionGuessService } from '../../definition-guess/definition-guess.service';
import { PageService } from '../page.service';
import { PlayAudioButtonComponent } from "../../../shared/play-audio-button/play-audio-button.component";

@Component({
    selector: 'app-page-edit-form',
    imports: [
        NgOptimizedImage,
        CommonModule,
        FormField,
        MatFormFieldModule,
        MatInputModule,
        MatProgressSpinnerModule,
        MatButtonModule,
        MatIconModule,
        MatToolbarModule,
        MatTabsModule,
        MatCardModule,
        MatTooltip,
        PlayAudioButtonComponent,
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
    canGenerateAudio = computed(() =>
        !this.isLoading() &&
        !this.isSaving() &&
        !this.form().dirty()
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

    loader = inject(FullscreenLoaderService);
    definitionGuessService = inject(DefinitionGuessService);

    addImage() {
        this.loader.show({ message: 'Generating & adding image...' });
        this.definitionGuessService.addImage(this.topicId(), this.pageId()).subscribe({
            next: (page) => this.model.update(m => ({ ...m, image_names: page.image_names })),
            complete: () => this.loader.hide(),
            error: () => this.loader.hide()
        });
    }

    generateAudio(texts: string[]) {
        this.loader.show({ message: 'Generating audio voices...' });
        this.definitionGuessService.generateAudio(this.topicId(), this.pageId(), texts).subscribe({
            next: (page) => {
                const cloned = structuredClone(page);
                this.originalModel.set(cloned);
                this.model.set(structuredClone(cloned));
            },
            complete: () => this.loader.hide(),
            error: (error) => {
                this.loader.hide(),
                this.snackBar.open('Error generating audio.', 'Close', { duration: 3000 });
                console.error('Error generating audio:', error);
            }
        });

    }

    removeImage(index: number) {
        this.model.update(m => ({ ...m, image_names: m.image_names?.filter((_, i) => i !== index) }));
        this.form().markAsDirty();
    }
}
