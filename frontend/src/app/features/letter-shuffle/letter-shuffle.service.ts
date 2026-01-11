import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

export interface LetterShuffleSetHeader {
  id: string;
  target_title: string;
  target_description: string;
  created_at: string;
  updated_at: string;
}

export interface LetterShuffleSet {
  id: string;
  target_title: string;
  target_description: string;
  native_title: string;
  native_description: string;
  created_at: string;
  updated_at: string;
  items: LetterShuffleItem[];
}

export interface LetterShuffleItem {
  target_phrase: string;
  target_description: string;
  target_phrase_audio_file_name: string;
  target_description_audio_file_name: string;
  phrase_image_name?: string;
  native_phrase: string;
  native_description: string;
  native_phrase_audio_file_name: string;
  native_description_audio_file_name: string;
}

@Injectable({
  providedIn: 'root'
})
export class LetterShuffleService {
  private endpoint = "/api/target-languages/en/letter-shuffles"

  constructor(private httpClient: HttpClient) { }

  getAll(): Observable<LetterShuffleSetHeader[]> {
    return this.httpClient.get<LetterShuffleSetHeader[]>(this.endpoint);
  }

  get(uid: string): Observable<LetterShuffleSet> {
    return this.httpClient.get<LetterShuffleSet>(
      `${this.endpoint}/${uid}/translations/pl`
    );
  }
}
