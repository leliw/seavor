import { Component, inject, OnInit } from '@angular/core';
import { LetterShuffleItem, LetterShuffleService, LetterShuffleSet, LetterShuffleSetHeader } from './letter-shuffle.service';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { SimpleDialogComponent } from '../../shared/simple-dialog/simple-dialog.component';


@Component({
    selector: 'app-letter-shuffle',
    imports: [
        MatDialogModule,
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
    question_audio!: HTMLAudioElement;
    description_audio!: HTMLAudioElement;


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
        this.question_audio = new Audio('/api/audio-files/' + this.item.question_audio_file_name);
        this.description_audio = new Audio('/api/audio-files/' + this.item.description_audio_file_name);
    }


    onClickLetter(index: number) {
        this.answer.push(this.letters[index]);
        this.letters.splice(index, 1);
        if (this.answer.join('') == this.item.question)
            this.onCorrect();
    }

    onClickAnswer(index: number) {
        this.letters.push(this.answer[index]);
        this.answer.splice(index, 1);
    }

    private dialog = inject(MatDialog);

    onCorrect() {
        this.question_audio.play().catch(err => console.error('Audio play error:', err));
        this.question_audio.addEventListener('ended', () => {
            this.description_audio.play().catch(err => console.error('Audio play error:', err));
        }, { once: true });
        this.dialog
            .open(SimpleDialogComponent, {
                data: {
                    title: $localize`Correct`,
                    message: `<b>${this.item.question}</b> - ${this.item.description}`,
                }
            })
            .afterClosed().subscribe(result => {
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
}
