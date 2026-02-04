import { Component } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from "@angular/material/button";
import { MatIcon } from "@angular/material/icon";
import {  RouterModule } from "@angular/router";

export interface TopicHeader {
    id: string;
    content_type: string;
    target_title: string;
    target_description: string;
    created_at?: string;
    updated_at?: string;
}


@Component({
    selector: 'app-topic-list',
    imports: [
    MatCardModule,
    MatButtonModule,
    MatIcon,
    RouterModule
],
    templateUrl: './topic-list.component.html',
    styleUrl: './topic-list.component.scss',
})
export class TopicListComponent {
    public topics: TopicHeader[] = [
        {
            id: 'semi-modal-verbs',
            content_type: 'info',
            target_title: 'Semi-modal verbs',
            target_description: 'A special group of verbs / expressions in English that behave partly like true modal verbs and partly like ordinary main verbs.'
        },
        {
            id: 'winter-holidays',
            content_type: 'letter-shuffle',
            target_title: 'Winter Holidays',
            target_description: 'Words and phrases related to Winter Holidays'
        },
    ]
}
