import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { CardService } from './card.service';
import { Card } from './card.model';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, FormsModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  cards: Card[] = [];
  newCardContent = '';

  constructor(private cardService: CardService) {}

  ngOnInit() {
    this.loadCards();
  }

  loadCards() {
    this.cardService.getCards().subscribe(cards => {
      this.cards = cards;
    });
  }

  addCard() {
    if (this.newCardContent.trim()) {
      this.cardService.addCard(this.newCardContent).subscribe(() => {
        this.newCardContent = '';
        this.loadCards();
      });
    }
  }

  deleteCard(cardId: number) {
    this.cardService.deleteCard(cardId).subscribe(() => {
      this.loadCards();
    });
  }

  downloadPdf() {
    this.cardService.downloadPdf().subscribe(blob => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'cards_book.pdf';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    });
  }
}
