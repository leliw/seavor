import { Component, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatIconModule } from "@angular/material/icon";

export interface InfoPageTab {
  target_title: string;
  target_content: string;
}

export interface InfoPage {
  id: string;
  target_title: string;
  target_description: string;
  tabs: InfoPageTab[];
  created_at?: string;
  updated_at?: string;
}

@Component({
  selector: 'app-info-page',
  imports: [
    MatExpansionModule,
    MatButtonModule,
    MatIconModule
],
  templateUrl: './info-page.component.html',
  styleUrl: './info-page.component.scss',
})
export class InfoPageComponent {
  public infoPage: InfoPage = {
    id: 'semi-modal-verbs',
    target_title: 'Semi-modal verbs',
    target_description: 'A special group of verbs / expressions in English that behave partly like true modal verbs and partly like ordinary main verbs.',
    tabs: [
      {
        target_title: "Semi-modals",
        target_content: '**Semi-modals** (also called semi-modal verbs, quasi-modals, marginal modals or lexical modals) are a special group of verbs / expressions in English that behave partly like true modal verbs (can, could, may, might, will, would, shall, should, must) and partly like ordinary main verbs.\n\n' +
          'They express similar ideas to modals — obligation, necessity, advice, ability, past habits etc. — but they are not pure modals.',
      },
      {
        target_title: "The most important differences compared to pure modal verbs",
        target_content: "x"
      },
      {
        target_title: "The most common semi-modals in British English",
        target_content: "x"
      }

    ]
  }

  step = signal(0);

  setStep(index: number) {
    this.step.set(index);
  }

  nextStep() {
    this.step.update(i => i + 1);
  }

  prevStep() {
    this.step.update(i => i - 1);
  }
}
