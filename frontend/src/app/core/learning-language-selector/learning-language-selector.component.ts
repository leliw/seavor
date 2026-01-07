import { Component } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { Router } from '@angular/router';
import { Language, LanguageService } from '../language-service.service';

@Component({
  selector: 'app-learning-language-selector',
    imports: [
        MatCardModule,
        MatButtonModule,
        MatIconModule,
    ],
  templateUrl: './learning-language-selector.component.html',
  styleUrl: './learning-language-selector.component.scss'
})
export class LearningLanguageSelectorComponent {
    learningLanguages: Language[] = [
        { code: 'en', nativeName: 'English', flag: '🇬🇧' },
        { code: 'es', nativeName: 'Español', flag: '🇪🇸' },
    ];

    constructor(
        private router: Router,
        private languageService: LanguageService
    ) { }

    selectLanguage(code: string): void {
        this.languageService.setLearningLanguage(code);
        this.navigateAfterSelection();
    }

    private navigateAfterSelection(): void {
        this.router.navigate(['/']);
    }
}
