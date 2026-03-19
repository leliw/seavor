import { Component, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { Router } from '@angular/router';
import { Language, LanguageService } from '../language.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { UserSettingsStore } from '../user-settings/user-settings.store';

interface Level {
    code: string;
    name: string;
}


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
    learningLevels: Level[] = [
        { code: 'A1', name: $localize`Breakthrough / Beginner` },
        { code: 'A2', name: $localize`Waystage / Elementary` },
        { code: 'B1', name: $localize`Threshold / Lower intermediate` },
        { code: 'B2', name: $localize`Vantage / Upper intermediate` },
        { code: 'C1', name: $localize`Operational proficiency / Advanced` },
        { code: 'C2', name: $localize`Mastery / Proficient` },
    ];

    userSettingsStorage = inject(UserSettingsStore);
    private _snackBar = inject(MatSnackBar);
    code?: string = undefined;

    constructor(
        private router: Router,
        private languageService: LanguageService
    ) { }

    selectLanguage(code: string): void {
        this.code = code;
    }
    selectLevel(level: string): void {
        if (this.code) {
            this.userSettingsStorage.updateSettings({ learning_language: this.code, learning_level: level });
            this.languageService.setLearningLanguage(this.code);
            this._snackBar.open($localize`Language & level changed`, $localize`Ok`, { duration: 2000 })
                .afterDismissed().subscribe(() => location.href = `/${this.code}/`);
        }
    }
}
