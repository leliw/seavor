import { Routes } from '@angular/router';
import { interfaceLanguageSelectedGuard, learningLanguageSelectedGuard } from './core/language.service';

export const routes: Routes = [
    { path: '', redirectTo: 'topics', pathMatch: 'full' },
    { path: 'login', title: "Login", loadComponent: () => import('./core/auth/login-form/login-form.component').then(m => m.LoginFormComponent) },
    {
        path: 'reset-password-request', title: "Reset password request",
        loadComponent: () => import('./core/auth/reset-password-request-form/reset-password-request-form.component').then(mod => mod.ResetPasswordRequestFormComponent)
    },
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
        path: 'repetitions',
        canActivate: [interfaceLanguageSelectedGuard, learningLanguageSelectedGuard],
        loadComponent: () => import("./core/navigation-bar/navigation-bar.component").then(m => m.NavigationBarComponent),
        children: [
            {
                path: '',
                loadComponent: () => import('./features/repetitions/repetitions-page/repetitions-page.component').then(m => m.RepetitionsPageComponent)
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
            },
            {
                path: 'gap-fill-choices/:id',
                loadComponent: () => import('./features/gap-fill-choice/gap-fill-choice.component').then(m => m.GapFillChoiceComponent)
            },
            {
                path: 'topics/:topic_id',
                loadComponent: () => import('./features/topics/topic-view/topic-view.component').then(m => m.TopicViewComponent)
            }

        ]
    },
];
