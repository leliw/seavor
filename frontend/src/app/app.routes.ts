import { Routes } from '@angular/router';

export const routes: Routes = [
    {
        path: '',
        redirectTo: 'letter-shuffle',
        pathMatch: 'full'
    },
    {
        path: 'letter-shuffle',
        loadComponent: () => import('./features/letter-shuffle/letter-shuffle.component').then(m => m.LetterShuffleComponent)
    }

];
