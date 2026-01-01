import { Component, OnInit } from '@angular/core';
import { LetterShuffleItem, LetterShuffleService, LetterShuffleSet, LetterShuffleSetHeader } from './letter-shuffle.service';


@Component({
  selector: 'app-letter-shuffle',
  imports: [],
  templateUrl: './letter-shuffle.component.html',
  styleUrl: './letter-shuffle.component.scss'
})
export class LetterShuffleComponent implements OnInit {
  private sets!: LetterShuffleSetHeader[];
  set!: LetterShuffleSet;
  itemIndex = 0;
  item!: LetterShuffleItem;
  letters!: string[];
  answer!: string[];

  constructor(private service: LetterShuffleService) {
  }

  ngOnInit(): void {
    this.service.getAll().subscribe(sets => {
      this.sets = sets;
      this.service.get(this.sets[0].id).subscribe(set => {
        this.set = set;
        for (let i = this.set.items.length - 1; i > 0; i--) {
          const j = Math.floor(Math.random() * (i + 1));
          [this.set.items[i], this.set.items[j]] = [this.set.items[j], this.set.items[i]];
        }
        this.itemIndex = 0;
        this.startItem();
      });
    });
  }

  startItem() {
    this.item = this.set.items[this.itemIndex];
    this.letters = this.item.question.split('');
    for (let i = this.letters.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [this.letters[i], this.letters[j]] = [this.letters[j], this.letters[i]];
    }
    this.answer = [];
  }


  onClickLetter(index: number) {
    this.answer.push(this.letters[index]);
    this.letters.splice(index, 1);
    if (this.answer.join('') == this.item.question)
      setTimeout(() => alert("Correct!"), 100);
  }

  onClickAnswer(index: number) {
    this.letters.push(this.answer[index]);
    this.answer.splice(index, 1);
  }

}
