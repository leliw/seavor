import { Component, input, output } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from "@angular/material/list";
import { MatToolbarModule } from "@angular/material/toolbar";
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-bottom-nav',
  imports: [
    RouterModule,
    MatToolbarModule,
    MatListModule,
    MatIconModule,
  ],
  templateUrl: './bottom-nav.component.html',
  styleUrl: './bottom-nav.component.scss',
})
export class BottomNavComponent {
  showHome = input(true);
  showRepetitions = input(false);
  showLearningLanguage = input(false);
  showSettings = input(false);

  showNextPage = input(false);
  showPreviousPage = input(false);
  showHint = input(false);
  showTranslate = input(false);

  disabledHint = input(false);
  disabledTranslate = input(false);


  nextPage = output();
  previousPage = output();
  hint = output();
  translate = output();
}
