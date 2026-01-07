import { Routes } from '@angular/router';
import { InterfaceLanguageSelectedGuard } from './core/interface-language-selected.guard';

export const routes: Routes = [
    {
        path: 'select-interface-language',
        loadComponent: () => import('./core/interface-language-selector/interface-language-selector.component').then(m => m.InterfaceLanguageSelectorComponent)
    },
    {
        path: '',
        canActivateChild: [InterfaceLanguageSelectedGuard],
        children: [
            { path: '', redirectTo: 'letter-shuffle', pathMatch: 'full' },
            {
                path: 'letter-shuffle',
                loadComponent: () => import('./features/letter-shuffle/letter-shuffle.component').then(m => m.LetterShuffleComponent)
            }
        ]
    }
];
