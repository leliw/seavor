import { Component, inject, OnInit } from '@angular/core';
import { MatButtonModule } from "@angular/material/button";
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { SimpleDialogComponent } from '../../shared/simple-dialog/simple-dialog.component';
import { LetterShuffleItem, LetterShuffleService, LetterShuffleSet, LetterShuffleSetHeader } from './letter-shuffle.service';


@Component({
    selector: 'app-letter-shuffle',
    imports: [
        MatDialogModule,
        MatButtonModule,
        MatIconModule,
    ],
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
    question!: string[];
    description!: string;
    image_src: string = "";
    question_audio!: HTMLAudioElement;
    description_audio!: HTMLAudioElement;
    hintIndex = 0;


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
        this.hintIndex = 0;
        this.image_src = '';
        this.item = this.set.items[this.itemIndex];
        this.image_src = '/api/images/' + this.item.question_image_name;
        this.question = this.item.question.split('');
        this.description = this.item.description;
        for (let i = 0; i < this.question.length; i++) {
            this.question[i] = this.question[i].toLocaleLowerCase();
            if (this.question[i] == ' ') {
                this.question[i] = "\xa0";
            }
        }
        this.letters = [...this.question];
        for (let i = this.letters.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [this.letters[i], this.letters[j]] = [this.letters[j], this.letters[i]];
        }
        this.answer = [];
        setTimeout(() => {
            this.question_audio = new Audio('/api/audio-files/' + this.item.question_audio_file_name);
            this.description_audio = new Audio('/api/audio-files/' + this.item.description_audio_file_name);
        }, 500);
    }


    onClickLetter(index: number) {
        this.answer.push(this.letters[index]);
        this.letters.splice(index, 1);
        if (this.answer.join('') == this.question.join(''))
            this.onCorrect();
    }

    onClickAnswer(index: number) {
        this.letters.push(this.answer[index]);
        this.answer.splice(index, 1);
    }

    private dialog = inject(MatDialog);

    onCorrect() {
        if (this.hintIndex == 0)
            this.hintIndex++;
        this.question_audio.play().catch(err => console.error('Audio play error:', err));
        if (this.hintIndex < 2) {
            this.question_audio.addEventListener('ended', () => {
                this.description_audio.play().catch(err => console.error('Audio play error:', err));
            }, { once: true });
        }
        this.dialog
            .open(SimpleDialogComponent, {
                data: {
                    title: $localize`Correct`,
                    message: `<b>${this.item.question}</b> - ${this.item.description}`,
                }
            })
            .afterClosed().subscribe(result => {
                this.question_audio?.pause();
                this.description_audio?.pause();
                this.itemIndex++;
                if (this.itemIndex >= this.set.items.length)
                    this.dialog.open(SimpleDialogComponent, {
                        data: {
                            title: $localize`Congratulations!`,
                            message: $localize`That's all!`
                        }
                    });
                else {
                    this.startItem();
                }
            });
    }

    showNextHint() {
        this.hintIndex++;
        if (this.hintIndex == 2) {
            this.description_audio.play().catch(err => console.error('Audio play error:', err));
        } else if (this.hintIndex > 2) {
            let correctLetters = 0;
            for (; correctLetters < this.answer.length; correctLetters++)
                if (this.answer[correctLetters] != this.question[correctLetters])
                    break;
            let hintLetter = this.hintIndex - 3;
            if (hintLetter < correctLetters)
                hintLetter = correctLetters;
            this.hintIndex = hintLetter + 3;
            for (let i = this.answer.length - 1; i >= hintLetter; i--)
                this.onClickAnswer(i);
            const index = this.letters.findIndex((letter, index) => letter == this.question[hintLetter]);
            this.onClickLetter(index);
        }
    }
}
