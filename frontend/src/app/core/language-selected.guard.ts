import { Injectable } from '@angular/core';
import { CanActivateChild, Router } from '@angular/router';
import { LanguageService } from './language-service.service';

@Injectable({
    providedIn: 'root'
})
export class LanguageSelectedGuard implements CanActivateChild {

    constructor(
        private languageService: LanguageService,
        private router: Router
    ) { }

    canActivateChild(): boolean {
        if (this.languageService.isInterfaceLanguageSelected()) {
            return true;
        }

        this.router.navigate(['/select-interface-language']);
        return false;
    }
}