import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { UserSettingsStore } from './user-settings/user-settings.store';

export const languageInterceptor: HttpInterceptorFn = (req, next) => {
    const userSettingsStore = inject(UserSettingsStore);
    const lang = userSettingsStore.settings().ui_language

    if (lang) {
        req = req.clone({
            setHeaders: {
                'Accept-Language': lang,
            }
        });
    }
    return next(req);
};
