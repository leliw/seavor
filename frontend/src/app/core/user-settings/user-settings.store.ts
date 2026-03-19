import { effect, inject, untracked } from '@angular/core';
import { tapResponse } from '@ngrx/operators';
import { patchState, signalStore, withHooks, withMethods, withState } from '@ngrx/signals';
import { rxMethod } from '@ngrx/signals/rxjs-interop';
import { pipe } from 'rxjs';
import { debounceTime, distinctUntilChanged, map, switchMap, tap } from 'rxjs/operators';
import { UserSettings } from './user-settings.model';
import { UserSettingsService } from './user-settings.service';
import { AuthStateService } from '../auth/auth-state.service';

type UserSettingsState = {
    settings: UserSettings;
    isLoading: boolean;
    error: string | null;
};

const initialState: UserSettingsState = {
    settings: {
        v: 1,
        ui_language: '',
        learning_language: '',
        learning_level: '',
    },
    isLoading: true,
    error: null,
};

export const UserSettingsStore = signalStore(
    withState(initialState),

    withMethods((store, service = inject(UserSettingsService)) => ({
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
                switchMap(({ changes, originalSettings }) =>
                    service.patch(changes).pipe(
                        tapResponse({
                            next: () => { },
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
        updateSetting: rxMethod<{ key: keyof UserSettings; value: any }>(
            pipe(
                debounceTime(300),
                distinctUntilChanged((prev, curr) =>
                    prev.key === curr.key && prev.value === curr.value
                ),
                map(({ key, value }) => {
                    const originalValue = store.settings()[key];
                    patchState(store, (state) => ({
                        settings: { ...state.settings, [key]: value },
                        error: null,
                    }));
                    return { key, value, originalValue };
                }),
                switchMap(({ key, value, originalValue }) =>
                    service.patch({ [key]: value }).pipe(
                        tapResponse({
                            next: () => { },
                            error: (err) => {
                                // Rollback
                                patchState(store, (state) => ({
                                    settings: { ...state.settings, [key]: originalValue },
                                    error: 'User settings update failed',
                                }));
                            },
                        })
                    )
                )
            )
        ),
    })),

    withHooks({
        onInit(store, authStateService = inject(AuthStateService)) {
            store.load();
            effect(() => {
                if (authStateService.isAuthenticated())
                    untracked(() => store.load());
            });
        },
    })
);
