import { Component, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { Language, LanguageService } from '../language.service';
import { UserSettingsStore } from '../user-settings/user-settings.store';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';


@Component({
    selector: 'app-interface-language-selector',
    imports: [
        MatCardModule,
        MatButtonModule,
        MatIconModule,
        MatSnackBarModule,
    ],
    templateUrl: './interface-language-selector.component.html',
    styleUrl: './interface-language-selector.component.scss'
})
export class InterfaceLanguageSelectorComponent {
    interfaceLanguages: Language[] = [
        { code: 'en', nativeName: 'English', flag: '🇬🇧' },
        { code: 'pl', nativeName: 'Polski', flag: '🇵🇱' },
        // { code: 'es', nativeName: 'Español', flag: '🇪🇸' },
        // { code: 'fr', nativeName: 'Français', flag: '🇫🇷' },
        // { code: 'de', nativeName: 'Deutsch', flag: '🇩🇪' },
        // { code: 'it', nativeName: 'Italiano', flag: '🇮🇹' },
        // { code: 'uk', nativeName: 'Українська', flag: '🇺🇦' },
        // { code: 'ru', nativeName: 'Путин, иди на xyй!', flag: '🇷🇺' },
        // { code: 'zh', nativeName: '中文', flag: '🇨🇳' },
        // { code: 'ar', nativeName: 'العربية', flag: '🇸🇦' },
    ];

    userSettingsStorage = inject(UserSettingsStore);
    private _snackBar = inject(MatSnackBar);


    constructor(
        private languageService: LanguageService
    ) { }

    selectLanguage(code: string): void {
        this.userSettingsStorage.updateSetting({ key: 'ui_language', value: code });
        this.languageService.setInterfaceLanguage(code);
        const basePath = location.pathname.replace(/^\/(pl|en|de)/, '');
        this._snackBar.open($localize`Language changed`, $localize`Ok`, { duration: 2000 })
            .afterDismissed().subscribe(() => location.href = `/${code}/`);
    }
}
