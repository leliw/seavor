import { ApplicationConfig, inject, provideAppInitializer, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';

import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { routes } from './app.routes';
import { ConfigService } from './core/config.service';
import { languageInterceptor } from './core/language.interceptor';

export const appConfig: ApplicationConfig = {
    providers: [
        provideAppInitializer(() => {
            const configService = inject(ConfigService);
            return configService.loadConfig();
        }),
        provideZoneChangeDetection({ eventCoalescing: true }),
        provideRouter(routes),
        provideHttpClient(withInterceptors([languageInterceptor])),
    ]
};
