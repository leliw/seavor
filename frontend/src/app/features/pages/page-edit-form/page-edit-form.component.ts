import { CommonModule } from '@angular/common';
import { Component, inject, input, linkedSignal } from '@angular/core';
import { rxResource } from '@angular/core/rxjs-interop';
import { PageService } from '../page.service';


@Component({
  selector: 'app-page-edit-form',
  imports: [
    CommonModule,
  ],
  templateUrl: './page-edit-form.component.html',
  styleUrl: './page-edit-form.component.scss',
})
export class PageEditFormComponent {
  topicId = input.required<string>();
  pageId = input.required<string>();
  service = inject(PageService);

  resource = rxResource({
    params: () => ({ topicId: this.topicId(), pageId: this.pageId() }),
    stream: ({ params }) => this.service.get(params.topicId, params.pageId)
  });
  model = linkedSignal(() => this.resource.value() ?? this.service.new());
}
