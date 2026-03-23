import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { DefinitionGuessComponent } from "../../definition-guess/definition-guess.component";
import { GapFillChoiceComponent } from "../../gap-fill-choice/gap-fill-choice.component";
import { RepetitionCardHeader, RepetitionService } from '../repetition.service';
import { SimpleDialogComponent } from '../../../shared/simple-dialog/simple-dialog.component';
import { MatDialog } from '@angular/material/dialog';
import { Router } from '@angular/router';
import { BottomNavComponent } from "../../../core/bottom-nav/bottom-nav.component";
import { UserSettingsStore } from '../../../core/user-settings/user-settings.store';

@Component({
  selector: 'app-repetition-view',
  imports: [
    CommonModule,
    GapFillChoiceComponent,
    DefinitionGuessComponent,
    BottomNavComponent
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
        // this.router.navigate(["/"])
      });
    }
  }
}
