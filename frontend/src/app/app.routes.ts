import { Routes } from '@angular/router';
import { interfaceLanguageSelectedGuard, learningLanguageSelectedGuard } from './core/language.service';

export const routes: Routes = [
    { path: '', redirectTo: 'topics', pathMatch: 'full' },
    {
        path: 'select-interface-language',
        loadComponent: () => import('./core/interface-language-selector/interface-language-selector.component').then(m => m.InterfaceLanguageSelectorComponent)
    },
    {
        path: 'select-learning-language', canActivate: [interfaceLanguageSelectedGuard],
        loadComponent: () => import('./core/learning-language-selector/learning-language-selector.component').then(m => m.LearningLanguageSelectorComponent)
    },
    {
        path: 'topics',
        canActivate: [interfaceLanguageSelectedGuard, learningLanguageSelectedGuard],
        loadComponent: () => import("./core/navigation-bar/navigation-bar.component").then(m => m.NavigationBarComponent),
        children: [
            {
                path: '',
                loadComponent: () => import('./features/topics/topic-list/topic-list.component').then(m => m.TopicListComponent)
            }
        ]
    },

    {
        path: '',
        canActivateChild: [interfaceLanguageSelectedGuard, learningLanguageSelectedGuard],
        children: [
            { path: '', redirectTo: 'topics', pathMatch: 'full' },
            {
                path: 'letter-shuffle/:id',
                loadComponent: () => import('./features/letter-shuffle/letter-shuffle.component').then(m => m.LetterShuffleComponent)
            }
        ]
    }
];
