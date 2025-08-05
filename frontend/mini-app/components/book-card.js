/**
 * Book Card Component
 * Displays book information in a consistent card format
 */

class BookCardComponent {
  constructor() {
    this.element = null;
  }

  create(book) {
    const card = document.createElement('div');
    card.className = 'book-card';
    card.dataset.bookId = book.id;
    
    const priceStatus = this.getPriceStatusClass(book.price_status);
    const approvalStatus = book.requires_approval ? 'approval-required' : '';
    
    card.innerHTML = `
      <div class="book-image">
        <img src="${book.cover_image || '/mybookshelf-logo.jpg'}" 
             alt="${book.title}" 
             onerror="this.src='/mybookshelf-logo.jpg'">
      </div>
      <div class="book-info">
        <h3 class="book-title">${this.escapeHtml(book.title)}</h3>
        <p class="book-author">${this.escapeHtml(book.author || 'Unknown Author')}</p>
        <div class="book-meta">
          <span class="price ${priceStatus}">$${book.price || 0}</span>
          <span class="status ${priceStatus}">${book.price_status || 'unknown'}</span>
        </div>
        <div class="book-actions">
          <button class="btn btn-primary" onclick="viewBook(${book.id})">
            View Details
          </button>
          ${book.requires_approval ? 
            `<button class="btn btn-warning" onclick="approveBook(${book.id})">
              Approve Price
            </button>` : ''
          }
        </div>
      </div>
      ${approvalStatus ? `<div class="approval-badge">⚠️ Approval Required</div>` : ''}
    `;

    this.element = card;
    return card;
  }

  getPriceStatusClass(status) {
    switch (status) {
      case 'in_stock': return 'status-success';
      case 'out_of_stock': return 'status-warning';
      case 'error': return 'status-error';
      default: return 'status-unknown';
    }
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  update(book) {
    if (!this.element) return;

    const priceElement = this.element.querySelector('.price');
    const statusElement = this.element.querySelector('.status');
    const approvalBadge = this.element.querySelector('.approval-badge');

    if (priceElement) {
      priceElement.textContent = `$${book.price || 0}`;
      priceElement.className = `price ${this.getPriceStatusClass(book.price_status)}`;
    }

    if (statusElement) {
      statusElement.textContent = book.price_status || 'unknown';
      statusElement.className = `status ${this.getPriceStatusClass(book.price_status)}`;
    }

    if (approvalBadge) {
      approvalBadge.style.display = book.requires_approval ? 'block' : 'none';
    }
  }

  destroy() {
    if (this.element) {
      this.element.remove();
      this.element = null;
    }
  }
}

export default BookCardComponent; 