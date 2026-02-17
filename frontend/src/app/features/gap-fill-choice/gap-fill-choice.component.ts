import { Component, inject, OnInit } from '@angular/core';
import { MatRadioModule } from '@angular/material/radio';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { GapFillChoiceExercise, GapFillChoiceService } from './gap-fill-choice.service';
import { FormsModule } from '@angular/forms';
import { MatToolbarModule } from "@angular/material/toolbar";
import { MatIconModule } from "@angular/material/icon";
import { MatListModule } from "@angular/material/list";

@Component({
  selector: 'app-gap-fill-choice',
  imports: [
    RouterModule,
    MatRadioModule,
    FormsModule,
    MatToolbarModule,
    MatIconModule,
    MatListModule
  ],
  templateUrl: './gap-fill-choice.component.html',
  styleUrl: './gap-fill-choice.component.scss',
})
export class GapFillChoiceComponent implements OnInit {
  private router = inject(Router);
  private service = inject(GapFillChoiceService);
  private route = inject(ActivatedRoute);

  id!: string | null;
  exercise!: GapFillChoiceExercise;
  answer: number | null = null;

  native = false;

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      this.id = params['id'];
      if (this.id) {
        this.service.get(this.id).subscribe(e => this.exercise = e);
      } else {
        this.router.navigate(['/topics']);
      }
    });
  }

  showHint() {
    throw new Error('Method not implemented.');
  }
}

