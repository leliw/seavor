import { effect, inject, untracked } from '@angular/core';
import { tapResponse } from '@ngrx/operators';
import { patchState, signalStore, withHooks, withMethods, withState } from '@ngrx/signals';
import { rxMethod } from '@ngrx/signals/rxjs-interop';
import { pipe } from 'rxjs';
import { concatMap, debounceTime, map, switchMap, tap } from 'rxjs/operators';
import { AuthStateService } from '../auth/auth-state.service';
import { DEFAULT_USER_SETTINGS, UserSettings } from './user-settings.model';
import { UserSettingsService } from './user-settings.service';

/**
 * State representing the user settings.
 */
type UserSettingsState = {
    settings: UserSettings;
    isLoading: boolean;
    error: string | null;
};

/**
 * Initial state for the user settings store.
 */
const initialState: UserSettingsState = {
    settings: DEFAULT_USER_SETTINGS,
    isLoading: true,
    error: null,
};

/**
 * Store for managing user settings, including loading and updating them.
 *
 * @example
 * \@Component({
 *   selector: 'app-settings',
 *   template: `
 *     <div *ngIf="store.isLoading()">Loading...</div>
 *     <div *ngIf="store.error()">Error: {{ store.error() }}</div>
 *     
 *     <mat-slide-toggle 
 *       [checked]="store.settings().darkMode" 
 *       (change)="toggleDarkMode($event.checked)">
 *       Dark Mode
 *     </mat-slide-toggle>
 *   `,
 *   providers: [UserSettingsStore]
 * })
 * export class SettingsComponent {
 *   protected readonly store = inject(UserSettingsStore);
 *
 *   toggleDarkMode(darkMode: boolean) {
 *     this.store.updateSettings({ darkMode });
 *   }
 * }
 */
export const UserSettingsStore = signalStore(
    withState(initialState),

    withMethods((store, service = inject(UserSettingsService)) => ({
        /**
         * Loads user settings from the backend.
         */
        load: rxMethod<void>(
            pipe(
                tap(() => patchState(store, { isLoading: true, error: null })),
                switchMap(() =>
                    service.get().pipe(
                        tapResponse({
                            next: (settings) => patchState(store, { settings, isLoading: false }),
                            error: (err) => patchState(store, {
                                error: 'User settings load failed',
                                isLoading: false
                            }),
                        })
                    )
                )
            )
        ),
        /**
         * Updates user settings with the provided changes.
         * Includes optimistic UI update and rollback on failure.
         * @param changes Partial settings to update.
         */
        updateSettings: rxMethod<Partial<UserSettings>>(
            pipe(
                debounceTime(400),
                map((changes) => {
                    const originalSettings = store.settings();
                    patchState(store, (state) => ({
                        settings: { ...state.settings, ...changes },
                        error: null,
                    }));
                    return { changes, originalSettings };
                }),
                concatMap(({ changes, originalSettings }) =>
                    service.patch(changes).pipe(
                        tapResponse({
                            next: (updatedSettings) => {
                                patchState(store, { settings: updatedSettings });
                            },
                            error: () => {
                                // Rollback
                                patchState(store, {
                                    settings: originalSettings,
                                    error: 'User settings update failed'
                                });
                            },
                        })
                    )
                )
            )
        ),
    })),

    withHooks({
        /**
         * Initializes the store and triggers loading when the user is authenticated.
         */
        onInit(store, authStateService = inject(AuthStateService)) {
            effect(() => {
                const isAuthenticated = authStateService.isAuthenticated();
                untracked(() => {
                    store.load();
                });
            });
        },
    })
);
