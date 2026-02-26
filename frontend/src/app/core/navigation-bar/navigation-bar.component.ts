import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatToolbarModule } from '@angular/material/toolbar';
import { RouterModule, RouterOutlet } from '@angular/router';
import { BottomNavComponent } from "../bottom-nav/bottom-nav.component";

@Component({
    selector: 'app-navigation-bar',
    imports: [
    CommonModule,
    RouterModule,
    RouterOutlet,
    MatToolbarModule,
    MatListModule,
    MatIconModule,
    BottomNavComponent
],
    templateUrl: './navigation-bar.component.html',
    styleUrl: './navigation-bar.component.scss',
})
export class NavigationBarComponent {

}
