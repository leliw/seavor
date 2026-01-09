import { Routes } from '@angular/router';
import { interfaceLanguageSelectedGuard, learningLanguageSelectedGuard } from './core/language.service';

export const routes: Routes = [
    {
        path: 'select-interface-language',
        loadComponent: () => import('./core/interface-language-selector/interface-language-selector.component').then(m => m.InterfaceLanguageSelectorComponent)
    },
    {
        path: 'select-learning-language', canActivate: [interfaceLanguageSelectedGuard],
        loadComponent: () => import('./core/learning-language-selector/learning-language-selector.component').then(m => m.LearningLanguageSelectorComponent)
    },
    {
        path: '',
        canActivateChild: [interfaceLanguageSelectedGuard, learningLanguageSelectedGuard],
        children: [
            { path: '', redirectTo: 'letter-shuffle', pathMatch: 'full' },
            {
                path: 'letter-shuffle',
                loadComponent: () => import('./features/letter-shuffle/letter-shuffle.component').then(m => m.LetterShuffleComponent)
            }
        ]
    }
];
