import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { LanguageService } from '../../core/language.service';


export interface Topic {
    id: string;
    content_id: string;
    content_type: string;
    language: string;
    levels: string[];
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
    constructor(private httpClient: HttpClient, private languageService: LanguageService) { }

    getEndpoint(): string {
        const targetLanguage = this.languageService.getLearningLanguage();
        const nativeLanguage = this.languageService.getInterfaceLanguage();
        const level = "A1"
        return `/api/native-topics/${targetLanguage}/${level}/${nativeLanguage}`;
    }

    getAll(): Observable<Topic[]> {
        return this.httpClient.get<Topic[]>(this.getEndpoint());
    }
    getPages(topic_id: string): Observable<PageHeader[]> {
        return this.httpClient.get<PageHeader[]>(`${this.getEndpoint()}/${topic_id}/pages`);
    }
}
