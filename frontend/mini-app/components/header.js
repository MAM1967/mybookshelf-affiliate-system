/**
 * Header Component for Admin Dashboard
 * Provides consistent branding and navigation
 */

class HeaderComponent {
  constructor() {
    this.element = null;
  }

  create() {
    const header = document.createElement('div');
    header.className = 'header';
    header.innerHTML = `
      <h1>📚 MyBookshelf Admin</h1>
      <p>Christian Leadership Book Management & Affiliate Marketing</p>
      <div class="header-stats">
        <span class="stat">
          <strong id="total-books">0</strong> Books
        </span>
        <span class="stat">
          <strong id="pending-approvals">0</strong> Pending
        </span>
        <span class="stat">
          <strong id="revenue-today">$0</strong> Today
        </span>
      </div>
    `;

    this.element = header;
    return header;
  }

  updateStats(stats) {
    if (!this.element) return;

    const totalBooks = this.element.querySelector('#total-books');
    const pendingApprovals = this.element.querySelector('#pending-approvals');
    const revenueToday = this.element.querySelector('#revenue-today');

    if (totalBooks) totalBooks.textContent = stats.totalBooks || 0;
    if (pendingApprovals) pendingApprovals.textContent = stats.pendingApprovals || 0;
    if (revenueToday) revenueToday.textContent = `$${stats.revenueToday || 0}`;
  }

  destroy() {
    if (this.element) {
      this.element.remove();
      this.element = null;
    }
  }
}

export default HeaderComponent; 