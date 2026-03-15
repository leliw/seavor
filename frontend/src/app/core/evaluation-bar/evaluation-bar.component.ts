import { Component, output } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatToolbarModule } from '@angular/material/toolbar';

@Component({
    selector: 'app-evaluation-bar',
    imports: [
        MatToolbarModule,
        MatListModule,
        MatIconModule,
    ],
    templateUrl: './evaluation-bar.component.html',
    styleUrl: './evaluation-bar.component.scss',
})
export class EvaluationBarComponent {
    evaluation = output<number>();
}
