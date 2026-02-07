import { Component, OnInit } from '@angular/core';
import { MatButtonModule } from "@angular/material/button";
import { MatCardModule } from '@angular/material/card';
import { MatIcon } from "@angular/material/icon";
import { RouterModule } from "@angular/router";
import { Topic, TopicService } from '../topic.service';


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
export class TopicListComponent implements OnInit {
    public topics!: Topic[];

    constructor(private topicService: TopicService) { }

    ngOnInit(): void {
        this.topicService.getAll().subscribe(topics => {
            this.topics = topics;
        });
    }
}
