import { Component } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { Router } from '@angular/router';
import { Language, LanguageService } from '../language.service';


@Component({
    selector: 'app-interface-language-selector',
    imports: [
        MatCardModule,
        MatButtonModule,
        MatIconModule,
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

    constructor(
        private router: Router,
        private languageService: LanguageService
    ) { }

    selectLanguage(code: string): void {
        this.languageService.setInterfaceLanguage(code);
        const basePath = location.pathname.replace(/^\/(pl|en|de)/, '');
        location.href = `/${code}/`;
    }
}