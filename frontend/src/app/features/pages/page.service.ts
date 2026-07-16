import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { DefinitionGuessExercise } from '../definition-guess/definition-guess.service';




@Injectable({
    providedIn: 'root',
})
export class PageService {
    private httpClient = inject(HttpClient);

    new(): DefinitionGuessExercise {
        return {
            id: '',
            type: '',
            language: '',
            level: '',
            phrase: '',
            definition: '',
            hint: '',
            explanation: '',
            sentences: [],
            alternatives: [],
            distractors: [],
        }
    }

    create(topicId: string, data: Partial<DefinitionGuessExercise>): Observable<void> {
        return this.httpClient.post<void>(`/api/topics/${topicId}/pages`, data);
    }

    get(topicId: string, pageId: string): Observable<DefinitionGuessExercise> {
        return this.httpClient.get<DefinitionGuessExercise>(`/api/topics/${topicId}/pages/${pageId}`);
    }

    patch(topicId: string, pageId: string, data: Partial<DefinitionGuessExercise>): Observable<void> {
        return this.httpClient.patch<void>(`/api/topics/${topicId}/pages/${pageId}`, data);
    }

    delete(topicId: string, pageId: string): Observable<void> {
        return this.httpClient.delete<void>(`/api/topics/${topicId}/pages/${pageId}`);
    }

    addImage(topicId: string, pageId: string): Observable<void> {
        return this.httpClient.post<void>(`/api/topics/${topicId}/pages/${pageId}/generate-image`, {});
    }

    evaluate(topicId: string, pageId: string, rate: number): Observable<void> {
        return this.httpClient.post<void>(`/api/topics/${topicId}/pages/${pageId}/evaluate`, { rating: rate });
    }
}
