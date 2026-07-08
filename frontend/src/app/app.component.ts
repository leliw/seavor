import { CommonModule } from '@angular/common';
import { Component, inject, ChangeDetectionStrategy } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { TaskService } from './shared/task.service';
import { MatProgressBarModule } from '@angular/material/progress-bar';

@Component({
    selector: 'app-root',
    imports: [CommonModule, RouterOutlet, MatProgressBarModule],
    templateUrl: './app.component.html',
    changeDetection: ChangeDetectionStrategy.Eager,
    styleUrl: './app.component.scss'
})
export class AppComponent {
    taskService = inject(TaskService);
}
