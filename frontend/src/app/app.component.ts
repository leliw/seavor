import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { ConfigService } from './core/config.service';
import { Observable } from 'rxjs';
import { CommonModule } from '@angular/common';

@Component({
    selector: 'app-root',
    imports: [CommonModule, RouterOutlet],
    templateUrl: './app.component.html',
    styleUrl: './app.component.scss'
})
export class AppComponent {
    title = 'Seavor';
    version$: Observable<string>;

    constructor(private configService: ConfigService) {
        this.version$ = this.configService.getConfigValue$("version");
    }
}
