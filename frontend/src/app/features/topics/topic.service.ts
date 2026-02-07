import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { LanguageService } from '../../core/language.service';


export interface Topic {
  id: string;
  content_id: string;
  content_type: string;
  target_language_code: string;
  levels: string[];
  target_title: string;
  target_description: string;
  native_language_code: string;
  native_title: string;
  native_description: string;
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
    return `/api/topics/${targetLanguage}/${level}/${nativeLanguage}`;
  }

  getAll(): Observable<Topic[]> {
    return this.httpClient.get<Topic[]>(this.getEndpoint());
  }
}
