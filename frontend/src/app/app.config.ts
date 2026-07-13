import { ApplicationConfig, inject, provideAppInitializer, provideZoneChangeDetection } from '@angular/core';
import { provideRouter, withComponentInputBinding } from '@angular/router';

import { IMAGE_LOADER, ImageLoaderConfig } from '@angular/common';
import { provideHttpClient, withInterceptors, withXhr } from '@angular/common/http';
import { routes } from './app.routes';
import { authInterceptor } from './core/auth/auth.interceptor';
import { ConfigService } from './core/config.service';
import { languageInterceptor } from './core/language.interceptor';
import { UserSettingsStore } from './core/user-settings/user-settings.store';
import { RepetitionService } from './features/repetitions/repetition.service';


export const customImageLoader = (config: ImageLoaderConfig) => {
    return `${config.src}?width=${config.width ?? 800}`;
};

export const appConfig: ApplicationConfig = {
    providers: [
        provideAppInitializer(() => {
            const configService = inject(ConfigService);
            return configService.loadConfig();
        }),
        provideZoneChangeDetection({ eventCoalescing: true }),
        provideRouter(routes, withComponentInputBinding()),
        provideHttpClient(withXhr(), withInterceptors([languageInterceptor, authInterceptor])),
        { provide: IMAGE_LOADER, useValue: customImageLoader },
        UserSettingsStore,
        RepetitionService,
    ]
};
