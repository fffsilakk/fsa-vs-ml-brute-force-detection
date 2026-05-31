// ========================================
// FSA BRUTE FORCE DETECTION SYSTEM
// JavaScript untuk handling interaksi UI
// ========================================

console.log("FSA Detection System Loaded");

// ========================================
// BLOCKED PAGE - COUNTDOWN TIMER
// ========================================

const BlockedPage = {
  timer: null,
  countdownElement: null,
  blockedUntil: null,

  init() {
    this.countdownElement = document.getElementById("countdownTimer");

    if (this.countdownElement) {
      const blockedUntilStr = this.countdownElement.getAttribute("data-until");

      if (blockedUntilStr) {
        // Parse datetime string (format: 2024-01-15 10:30:45.123456)
        this.blockedUntil = new Date(blockedUntilStr.replace(" ", "T"));
        this.startCountdown();
      }
    }
  },

  startCountdown() {
    // Update immediately
    this.updateCountdown();

    // Then update every second
    this.timer = setInterval(() => {
      this.updateCountdown();
    }, 1000);
  },

  updateCountdown() {
    const now = new Date();
    const diff = this.blockedUntil - now;

    if (diff <= 0) {
      // Time's up - redirect to login
      clearInterval(this.timer);
      this.showUnblockMessage();

      setTimeout(() => {
        window.location.href = "/login";
      }, 2000);

      return;
    }

    // Calculate minutes and seconds
    const minutes = Math.floor(diff / 60000);
    const seconds = Math.floor((diff % 60000) / 1000);

    // Format with leading zeros
    const minutesStr = String(minutes).padStart(2, "0");
    const secondsStr = String(seconds).padStart(2, "0");

    // Update display
    const minutesSpan = document.getElementById("minutes");
    const secondsSpan = document.getElementById("seconds");

    if (minutesSpan && secondsSpan) {
      minutesSpan.textContent = minutesStr;
      secondsSpan.textContent = secondsStr;
    }
  },

  showUnblockMessage() {
    if (this.countdownElement) {
      this.countdownElement.innerHTML =
        '<span style="color: var(--success);">✓ Akun Aktif Kembali</span>';
    }
  },
};

// ========================================
// DASHBOARD - AUTO REFRESH & STATS
// ========================================

const Dashboard = {
  refreshInterval: 30000, // 30 seconds
  autoRefreshTimer: null,

  init() {
    console.log("Dashboard initialized");
    this.setupAutoRefresh();
    this.addTableInteractions();
  },

  setupAutoRefresh() {
    // Auto refresh every 30 seconds
    this.autoRefreshTimer = setInterval(() => {
      console.log("Auto-refreshing dashboard...");
      this.refreshStats();
      this.refreshLogs();
    }, this.refreshInterval);
  },

  async refreshStats() {
    try {
      // Get current username from page
      const welcomeText = document.querySelector(".welcome-text");
      if (!welcomeText) return;

      const username = welcomeText.textContent.split(":")[1]?.trim();
      if (!username) return;

      const response = await fetch(`/api/stats/${username}`);
      const stats = await response.json();

      // Update stat cards
      this.updateStatCard("total_attempts", stats.total_attempts);
      this.updateStatCard("failed_attempts", stats.failed_attempts);
      this.updateStatCard("successful_attempts", stats.successful_attempts);
      this.updateStatCard("current_state", stats.current_state);

      console.log("Stats refreshed:", stats);
    } catch (error) {
      console.error("Error refreshing stats:", error);
    }
  },

  updateStatCard(type, value) {
    const card = document.querySelector(`[data-stat="${type}"]`);
    if (card) {
      const valueElement = card.querySelector(".stat-value");
      if (valueElement) {
        // Animate value change
        valueElement.style.transform = "scale(1.1)";
        valueElement.textContent = value;

        setTimeout(() => {
          valueElement.style.transform = "scale(1)";
        }, 200);
      }
    }
  },

  async refreshLogs() {
    try {
      const response = await fetch("/api/logs");
      const logs = await response.json();

      const tbody = document.querySelector(".logs-table tbody");
      if (!tbody) return;

      // Clear and repopulate table
      tbody.innerHTML = "";

      logs.slice(0, 50).forEach((log) => {
        const row = this.createLogRow(log);
        tbody.appendChild(row);
      });

      console.log("Logs refreshed");
    } catch (error) {
      console.error("Error refreshing logs:", error);
    }
  },

  createLogRow(log) {
    const row = document.createElement("tr");

    const statusClass = log.success ? "status-success" : "status-failed";
    const statusText = log.success ? "✓ Berhasil" : "✗ Gagal";

    let stateClass = "normal";
    if (log.state === "suspicious") stateClass = "suspicious";
    if (log.state === "blocked") stateClass = "blocked";

    row.innerHTML = `
      <td>${this.escapeHtml(log.username)}</td>
      <td class="${statusClass}">${statusText}</td>
      <td>${this.escapeHtml(log.ip_address)}</td>
      <td><span class="state-label ${stateClass}">${this.escapeHtml(
      log.state
    )}</span></td>
      <td>${this.escapeHtml(log.message)}</td>
      <td>${this.formatTimestamp(log.timestamp)}</td>
    `;

    return row;
  },

  escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  },

  formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString("id-ID", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  },

  addTableInteractions() {
    const rows = document.querySelectorAll(".logs-table tbody tr");
    rows.forEach((row) => {
      row.addEventListener("mouseenter", () => {
        row.style.backgroundColor = "rgba(255, 255, 255, 0.05)";
      });

      row.addEventListener("mouseleave", () => {
        row.style.backgroundColor = "";
      });
    });
  },
};

// ========================================
// LOGIN PAGE - STATE ANIMATION - NEW!
// ========================================

const LoginStateAnimation = {
  init() {
    console.log("Login state animation initialized");

    // Animate active state badge on page load
    const activeBadge = document.querySelector(".state-badge.active");
    if (activeBadge) {
      // Add pop-in animation after short delay
      setTimeout(() => {
        activeBadge.style.animation =
          "popIn 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55)";
      }, 300);
    }

    // Add form submission animation
    this.setupFormAnimation();
  },

  setupFormAnimation() {
    const form = document.querySelector(".login-form");
    if (!form) return;

    form.addEventListener("submit", (e) => {
      const button = form.querySelector(".btn-login");
      if (button) {
        button.innerHTML =
          '<span>Memproses...</span><span class="btn-icon">⏳</span>';
        button.disabled = true;
      }
    });
  },
};

// ========================================
// UTILITY FUNCTIONS
// ========================================

const Utils = {
  // Smooth scroll to element
  scrollTo(element, duration = 300) {
    element.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  },

  // Show notification (if needed for future features)
  notify(message, type = "info") {
    console.log(`[${type.toUpperCase()}] ${message}`);
    // TODO: Implement toast notification system
  },
};

// ========================================
// INITIALIZATION ON PAGE LOAD
// ========================================

document.addEventListener("DOMContentLoaded", () => {
  console.log("Page loaded, initializing components...");

  // Initialize blocked page countdown
  if (document.getElementById("countdownTimer")) {
    BlockedPage.init();
  }

  // Initialize dashboard
  if (document.querySelector(".dashboard-container")) {
    Dashboard.init();
  }

  // Initialize login page animations - NEW!
  if (document.querySelector(".login-form")) {
    LoginStateAnimation.init();
  }

  // Add smooth transitions to all buttons
  document
    .querySelectorAll("button, .btn-login, .btn-logout, .btn-back")
    .forEach((button) => {
      button.style.transition = "all 0.3s ease";
    });

  console.log("All components initialized successfully");
});

// ========================================
// CLEANUP ON PAGE UNLOAD
// ========================================

window.addEventListener("beforeunload", () => {
  // Clear dashboard auto-refresh timer
  if (Dashboard.autoRefreshTimer) {
    clearInterval(Dashboard.autoRefreshTimer);
  }

  // Clear blocked page countdown timer
  if (BlockedPage.timer) {
    clearInterval(BlockedPage.timer);
  }
});
