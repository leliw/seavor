import { inject, Injectable } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { BehaviorSubject, Observable } from 'rxjs';

const UI_LANGUAGE_KEY = 'app-ui-language';
const LEARNING_LANGUAGE_KEY = 'app-learning-language';


export interface Language {
    code: string;
    nativeName: string;
    englishName?: string;
    flag: string;
}

@Injectable({
    providedIn: 'root'
})
export class LanguageService {
    private currentInterfaceLanguageSubject = new BehaviorSubject<string | null>(null);
    public currentInterfaceLanguage$ = this.currentInterfaceLanguageSubject.asObservable();
    private currentLearningLanguageSubject = new BehaviorSubject<string | null>(null);


    constructor() {
        const savedInterfaceLanguage = localStorage.getItem(UI_LANGUAGE_KEY);
        if (savedInterfaceLanguage) {
            this.currentInterfaceLanguageSubject.next(savedInterfaceLanguage);
        }
    }

    setInterfaceLanguage(code: string): void {
        if (!code) {
            return;
        }
        localStorage.setItem(UI_LANGUAGE_KEY, code);
        this.currentInterfaceLanguageSubject.next(code);
        $localize.locale = code;
    }

    getInterfaceLanguage(): string | null {
        return this.currentInterfaceLanguageSubject.value;
    }

    getCurrentLanguageObservable(): Observable<string | null> {
        return this.currentInterfaceLanguage$;
    }

    clearInterfaceLanguage(): void {
        localStorage.removeItem(UI_LANGUAGE_KEY);
        this.currentInterfaceLanguageSubject.next(null);
    }

    isInterfaceLanguageSelected(): boolean {
        return this.getInterfaceLanguage() !== null;
    }

    setLearningLanguage(code: string): void {
        if (!code) {
            return;
        }
        localStorage.setItem(LEARNING_LANGUAGE_KEY, code);
        this.currentLearningLanguageSubject.next(code);
    }

    getLearningLanguage(): string | null {
        return this.currentLearningLanguageSubject.value;
    }

    isLearningLanguageSelected(): boolean {
        return this.getLearningLanguage() !== null;

    }
}

export const interfaceLanguageSelectedGuard: CanActivateFn = (route, state) => {
    const languageService = inject(LanguageService);
    const router = inject(Router)
    if (languageService.isInterfaceLanguageSelected()) {
        return true;
    } else {

        router.navigate(['/select-interface-language']);
        return false;
    }
}

export const learningLanguageSelectedGuard: CanActivateFn = (route, state) => {
    const languageService = inject(LanguageService);
    const router = inject(Router)
    if (languageService.isLearningLanguageSelected()) {
        return true;
    } else {

        router.navigate(['/select-learning-language']);
        return false;
    }
};