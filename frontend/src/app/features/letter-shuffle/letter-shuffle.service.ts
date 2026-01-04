import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

export interface LetterShuffleSetHeader {
  id: string;
  title: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface LetterShuffleSet {
  id: string;
  title: string;
  description: string;
  created_at: string;
  updated_at: string;
  items: LetterShuffleItem[];
}

export interface LetterShuffleItem {
  question: string;
  description: string;
  question_audio_file_name: string;
  description_audio_file_name: string;
  question_image_name?: string;
}

@Injectable({
  providedIn: 'root'
})
export class LetterShuffleService {
  private endpoint = "/api/letter-shuffles"

  constructor(private httpClient: HttpClient) { }

  getAll(): Observable<LetterShuffleSetHeader[]> {
    return this.httpClient.get<LetterShuffleSetHeader[]>(this.endpoint);
  }

  get(uid: string): Observable<LetterShuffleSet> {
    return this.httpClient.get<LetterShuffleSet>(
      `${this.endpoint}/${uid}`
    );
  }
}
