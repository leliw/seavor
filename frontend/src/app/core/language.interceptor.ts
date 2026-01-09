import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { LanguageService } from './language.service';

export const languageInterceptor: HttpInterceptorFn = (req, next) => {
  const languageService = inject(LanguageService);
  const lang = languageService.getInterfaceLanguage();

  if (lang) {
    req = req.clone({
      setHeaders: {
        'Accept-Language': lang
      }
    });
  }
  return next(req);
};
