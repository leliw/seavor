import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog } from '@angular/material/dialog';
import { MatIconModule } from "@angular/material/icon";
import { MatMenuModule } from "@angular/material/menu";
import { MatToolbarModule } from "@angular/material/toolbar";
import { Router, RouterModule } from '@angular/router';
import { BottomNavComponent } from "../../../core/bottom-nav/bottom-nav.component";
import { UserSettingsStore } from '../../../core/user-settings/user-settings.store';
import { FullscreenLoaderService } from '../../../shared/fullscreen-loader.service';
import { SimpleDialogComponent } from '../../../shared/simple-dialog/simple-dialog.component';
import { DefinitionGuessComponent } from "../../definition-guess/definition-guess.component";
import { GapFillChoiceComponent } from "../../gap-fill-choice/gap-fill-choice.component";
import { RepetitionCardHeader, RepetitionService } from '../repetition.service';
import { DefinitionGuessService } from '../../definition-guess/definition-guess.service';


@Component({
  selector: 'app-repetition-view',
  imports: [
    CommonModule,
    GapFillChoiceComponent,
    DefinitionGuessComponent,
    BottomNavComponent,
    MatToolbarModule,
    MatIconModule,
    MatMenuModule,
    MatButtonModule,
    RouterModule,
  ],
  templateUrl: './repetition-view.component.html',
  styleUrl: './repetition-view.component.scss',
})
export class RepetitionViewComponent {
  router = inject(Router);
  dialog = inject(MatDialog);
  repetitionService = inject(RepetitionService)
  userSettingsStore = inject(UserSettingsStore)

  repetitions!: RepetitionCardHeader[];
  repetitionIndex: number = 0;
  repetition: RepetitionCardHeader | undefined;

  ngOnInit(): void {
    this.repetitionService.getOverdue().subscribe(reps => {
      this.repetitions = reps;
      this.repetitionIndex = 0;
      this.repetition = this.repetitions[this.repetitionIndex];
    })
  }

  onPreviousPage() {
    if (this.repetitionIndex > 0) {
      this.repetitionIndex -= 1;
    }
  }

  onNextPage() {
    if (this.repetitionIndex + 1 < this.repetitions.length) {
      this.repetitionIndex += 1;
      this.repetition = this.repetitions[this.repetitionIndex];
    } else {
      this.dialog.open(SimpleDialogComponent, {
        data: {
          title: $localize`Congratulations!`,
          message: $localize`That's all!`
        }
      }).afterClosed().subscribe(() => {
        this.repetitions = [];
        this.repetition = undefined;
        this.repetitionService.getSchedule().subscribe();
      });
    }
  }

  loader = inject(FullscreenLoaderService);
  definitionGuessService = inject(DefinitionGuessService);

  addImage() {
    if (!this.repetition || this.repetition.type != 'definition-guess') {
      return;
    }
    this.loader.show({ message: 'Generating & adding image...' });
    this.definitionGuessService.addImage(this.repetition.level, this.repetition.topic_id, this.repetition.page_id).subscribe({
      complete: () => this.loader.hide(),
      error: () => this.loader.hide()
    });
  }
}
