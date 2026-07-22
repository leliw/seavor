export interface UserSettings {
    ui_language: string;
    learning_language: string
    learning_level: string
}

export const DEFAULT_USER_SETTINGS: UserSettings = {
    ui_language: 'pl',
    learning_language: 'en',
    learning_level: 'A1',
};
