import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

const UI_LANGUAGE_KEY = 'app-ui-language';

export interface AppLanguage {
    code: string;
    nativeName: string;
    englishName?: string;
    flag: string;
}

@Injectable({
    providedIn: 'root'
})
export class LanguageService {
    private currentLanguageSubject = new BehaviorSubject<string | null>(null);
    public currentLanguage$ = this.currentLanguageSubject.asObservable();

    constructor() {
        const savedLanguage = localStorage.getItem(UI_LANGUAGE_KEY);
        if (savedLanguage) {
            this.currentLanguageSubject.next(savedLanguage);
        }
    }

    setInterfaceLanguage(code: string): void {
        if (!code) {
            return;
        }
        localStorage.setItem(UI_LANGUAGE_KEY, code);
        this.currentLanguageSubject.next(code);

        // Tutaj możesz dodać integrację z ngx-translate lub @angular/localize
        // Przykład dla ngx-translate:
        // this.translate.use(code);

        // Przykład dla @angular/localize:
        // import('@angular/localize/init') – potem $localize.locale = code;
    }

    getInterfaceLanguage(): string | null {
        return this.currentLanguageSubject.value;
    }

    getCurrentLanguageObservable(): Observable<string | null> {
        return this.currentLanguage$;
    }

    clearInterfaceLanguage(): void {
        localStorage.removeItem(UI_LANGUAGE_KEY);
        this.currentLanguageSubject.next(null);
    }

    isInterfaceLanguageSelected(): boolean {
        return this.getInterfaceLanguage() !== null;
    }
}