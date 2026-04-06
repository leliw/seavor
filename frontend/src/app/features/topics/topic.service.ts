import { HttpClient } from '@angular/common/http';
import { computed, inject, Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { UserSettingsStore } from '../../core/user-settings/user-settings.store';


export interface Topic {
    id: string;
    content_id: string;
    content_type: string;
    language: string;
    level: string;
    type: string;
    title: string;
    description: string;
    native_language_code: string;
    native_title: string;
    native_description: string;
    image_name?: string;
    created_at?: string;
    updated_at?: string;
}

export interface PageHeader {
    id: string;
    order: number;
    type: string;
    created_at?: string;
    updated_at?: string;
}

@Injectable({
    providedIn: 'root',
})
export class TopicService {
    private userSettingsStorage = inject(UserSettingsStore);
    private language = computed(() => this.userSettingsStorage.settings().learning_language);
    private level = computed(() => this.userSettingsStorage.settings().learning_level);
    private uiLanguage = computed(() => this.userSettingsStorage.settings().ui_language);

    constructor(private httpClient: HttpClient) { }

    getEndpoint(): string {
        return `/api/native-topics/${this.language()}/${this.level()}/${this.uiLanguage()}`;
    }

    getAll(): Observable<Topic[]> {
        return this.httpClient.get<Topic[]>(this.getEndpoint());
    }
    getPages(topic_id: string): Observable<PageHeader[]> {
        if (topic_id == "definition-guess") {
            return of([
                {
                    id: "id",
                    order: 1,
                    type: "definition-guess"
                }
            ]);
        }
        return this.httpClient.get<PageHeader[]>(`${this.getEndpoint()}/${topic_id}/pages`);
    }
}
