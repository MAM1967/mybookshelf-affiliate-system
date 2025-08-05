/**
 * Navigation Component for Admin Dashboard
 * Handles tab switching and navigation state
 */

class NavigationComponent {
  constructor() {
    this.element = null;
    this.activeTab = 'overview';
    this.onTabChange = null;
  }

  create() {
    const nav = document.createElement('div');
    nav.className = 'nav-tabs';
    nav.innerHTML = `
      <button class="nav-tab active" data-tab="overview">
        📊 Overview
      </button>
      <button class="nav-tab" data-tab="books">
        📚 Books
      </button>
      <button class="nav-tab" data-tab="approvals">
        ✅ Approvals
      </button>
      <button class="nav-tab" data-tab="pricing">
        💰 Pricing
      </button>
      <button class="nav-tab" data-tab="analytics">
        📈 Analytics
      </button>
      <button class="nav-tab" data-tab="settings">
        ⚙️ Settings
      </button>
    `;

    this.element = nav;
    this.bindEvents();
    return nav;
  }

  bindEvents() {
    if (!this.element) return;

    const tabs = this.element.querySelectorAll('.nav-tab');
    tabs.forEach(tab => {
      tab.addEventListener('click', (e) => {
        const tabName = e.target.dataset.tab;
        this.setActiveTab(tabName);
      });
    });
  }

  setActiveTab(tabName) {
    if (!this.element) return;

    // Update tab buttons
    const tabs = this.element.querySelectorAll('.nav-tab');
    tabs.forEach(tab => {
      tab.classList.remove('active');
      if (tab.dataset.tab === tabName) {
        tab.classList.add('active');
      }
    });

    // Update active tab
    this.activeTab = tabName;

    // Trigger callback
    if (this.onTabChange) {
      this.onTabChange(tabName);
    }
  }

  getActiveTab() {
    return this.activeTab;
  }

  destroy() {
    if (this.element) {
      this.element.remove();
      this.element = null;
    }
  }
}

export default NavigationComponent; 