import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { LanguageService } from '../../core/language.service';
import { Observable } from 'rxjs';

export interface InfoPageHeader {
  id: string;
  level: string;
}

export interface InfoPage {
  id: string;
  target_language: string;
  level: string;
  order: number;
  type: string
  title: string;
  content: string;
  image_url: string | undefined;
  native_title: string;
  native_content: string;
  created_at?: string;
  updated_at?: string;
}

@Injectable({
  providedIn: 'root',
})
export class InfoPageService {
  constructor(private httpClient: HttpClient, private languageService: LanguageService) { }

  getEndpoint(): string {
    const targetLanguage = this.languageService.getLearningLanguage();
    const nativeLanguage = this.languageService.getInterfaceLanguage();
    const level = "A1"
    return `/api/native-topics/${targetLanguage}/${level}/${nativeLanguage}`;
  }

  getAll(): Observable<InfoPageHeader[]> {
    return this.httpClient.get<InfoPageHeader[]>(this.getEndpoint());
  }

  get(topicId: string, uid: string): Observable<InfoPage> {
    return this.httpClient.get<InfoPage>(`${this.getEndpoint()}/${topicId}/pages/${uid}`);
  }

}
