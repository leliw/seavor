import { Component, inject, input, output } from '@angular/core';
import { MatBadgeModule } from '@angular/material/badge';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from "@angular/material/list";
import { MatToolbarModule } from "@angular/material/toolbar";
import { RouterModule } from '@angular/router';
import { RepetitionService } from '../../features/repetitions/repetition.service';
import { AuthService } from '../auth/auth.service';


@Component({
  selector: 'app-bottom-nav',
  imports: [
    RouterModule,
    MatToolbarModule,
    MatListModule,
    MatIconModule,
    MatBadgeModule,
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
  showCheck = input(false);
  showHint = input(false);
  showTranslate = input(false);

  disabledHint = input(false);
  disabledTranslate = input(false);


  nextPage = output();
  previousPage = output();
  check = output();
  hint = output();
  translate = output();

  authService = inject(AuthService);
  repetitionService = inject(RepetitionService);

  logout() {
    this.authService.logout().subscribe();
  }
}
