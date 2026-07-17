import { Component, output, ChangeDetectionStrategy, input } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatTooltipModule } from '@angular/material/tooltip';

@Component({
    selector: 'app-evaluation-bar',
    imports: [
        MatToolbarModule,
        MatListModule,
        MatIconModule,
        MatTooltipModule,
    ],
    templateUrl: './evaluation-bar.component.html',
    changeDetection: ChangeDetectionStrategy.Eager,
    styleUrl: './evaluation-bar.component.scss',
})
export class EvaluationBarComponent {
    showTranslate = input<boolean>(false);
    evaluation = output<number>();
    translate = output<void>();
}
