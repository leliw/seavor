import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { LanguageService } from '../../core/language.service';
import { Observable, of } from 'rxjs';

export interface Sentence {
    text_with_gap: string;
    gap_filler_form: string;
    audio_file_name?: string;
}

export interface AnswerOption {
    value: string;
    explanation?: string;
    audio_file_name?: string;
}

export interface DefinitionGuessExercise {
    id: string;
    language: string;
    level: string;

    phrase: string;
    description: string;
    sentences: Sentence[];

    alternatives: AnswerOption[];
    distractors: AnswerOption[];

    hint?: string;
    explanation?: string;

    phrase_audio_file_name?: string;
    description_audio_file_name?: string;
    hint_audio_file_name?: string;
    explanation_audio_file_name?: string;
}

@Injectable({
    providedIn: 'root',
})
export class DefinitionGuessService {
    constructor(private httpClient: HttpClient, private languageService: LanguageService) { }

    getEndpoint(): string {
        const language = this.languageService.getLearningLanguage();
        const nativeLanguage = this.languageService.getInterfaceLanguage();
        const level = "A1"
        return `/api/native-topics/${language}/${level}/${nativeLanguage}`;
    }

    get(topicId: string, uid: string): Observable<DefinitionGuessExercise> {
        if (topicId == "definition-guess")
            return of({
                id: "id",
                language: "en",
                level: "A1",
                phrase: "plain sailing",
                description: "to be easy and without problems",
                sentences: [
                    { text_with_gap: "Once we had finished all the legal paperwork, setting up the new business was ________.", gap_filler_form: "plain sailing" },
                    { text_with_gap: "The first half of the match was very difficult, but after they scored the second goal it was just ________.", gap_filler_form: "plain sailing" },
                    { text_with_gap: "Don't worry - the instructions are very clear and the assembly itself is ________.", gap_filler_form: "plain sailing" },
                    { text_with_gap: "Getting a visa used to be complicated, but these days for most European countries it's pretty much ________.", gap_filler_form: "plain sailing" }
                ],
                hint: "It is an expression that comes from sailing/ships.",
                explanation: "‘Plain sailing’ (British English) means a situation or task is easy and straightforward, with no difficulties or complications. \n\nIn American English the more common version is **‘smooth sailing’**.",
                alternatives: [
                    { value: "smooth sailing", explanation: "The most common alternative - especially frequent in American English and increasingly common in British English too." },
                    { value: "plain sailing from there on", explanation: "Very natural longer version - often used when describing the later part of a process." },
                    { value: "easy going", explanation: "Similar meaning but much weaker / less idiomatic in this exact context." },
                    { value: "plain sailing after that", explanation: "Natural and very common in spoken British English - adds time reference." }
                ],
                distractors: [
                    { value: "child's play", explanation: "Means something is very easy, but it usually refers to the activity itself being very simple - not necessarily that problems are absent." },
                    { value: "a piece of cake", explanation: "Very informal = very easy. It focuses more on simplicity than on lack of problems or obstacles." },
                    { value: "plain and simple", explanation: "Means clear and straightforward (about facts / instructions), but not used for describing a process or period of time." },
                    { value: "clear skies", explanation: "Not a real fixed phrase in this context - sounds logical but is not idiomatic English." },
                    { value: "smooth run", explanation: "Sounds similar, but is not a standard English idiom." }
                ],
            })
        else
            return this.httpClient.get<DefinitionGuessExercise>(`${this.getEndpoint()}/${topicId}/pages/${uid}`);
    }
}
