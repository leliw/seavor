import { Component, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { Router } from '@angular/router';
import { Language, LanguageService } from '../language.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { UserSettingsStore } from '../user-settings/user-settings.store';

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
        { code: 'fr', nativeName: 'Français', flag: '🇫🇷' },
        { code: 'de', nativeName: 'Deutsch', flag: '🇩🇪' },

    ];

    userSettingsStorage = inject(UserSettingsStore);
    private _snackBar = inject(MatSnackBar);

    constructor(
        private router: Router,
        private languageService: LanguageService
    ) { }

    selectLanguage(code: string): void {
        this.userSettingsStorage.updateSettings({ learning_language: code, learning_level: 'B1' });
        this.languageService.setLearningLanguage(code);
        this._snackBar.open($localize`Language changed`, $localize`Ok`, { duration: 2000 })
            .afterDismissed().subscribe(() => location.href = `/${code}/`);
    }
}
