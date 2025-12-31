import { Component, OnInit } from '@angular/core';

interface LetterShuffleItem {
  question: string;
  description: string;
}



@Component({
  selector: 'app-letter-shuffle',
  imports: [],
  templateUrl: './letter-shuffle.component.html',
  styleUrl: './letter-shuffle.component.scss'
})
export class LetterShuffleComponent implements OnInit {

  item: LetterShuffleItem = {
    question: "carols",
    description: "kolędy śpiewane w okresie świątecznym"
  }

  letters!: string[];
  answer!: string[];


  constructor() { }

  ngOnInit(): void {
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
