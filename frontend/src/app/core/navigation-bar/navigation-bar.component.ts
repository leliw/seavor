import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatToolbarModule } from '@angular/material/toolbar';
import { RouterModule, RouterOutlet } from '@angular/router';

@Component({
    selector: 'app-navigation-bar',
    imports: [
        CommonModule,
        RouterModule,
        RouterOutlet,
        MatToolbarModule,
        MatListModule,
        MatIconModule,
    ],
    templateUrl: './navigation-bar.component.html',
    styleUrl: './navigation-bar.component.scss',
})
export class NavigationBarComponent {

}
