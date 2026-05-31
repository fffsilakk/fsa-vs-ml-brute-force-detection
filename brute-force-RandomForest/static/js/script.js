// ==========================================================================
// RANDOM FOREST BRUTE FORCE DETECTION SYSTEM
// JavaScript untuk handling interaksi UI & Auto-Refresh Data Klasifikasi Ensemble
// ==========================================================================

console.log("Random Forest Ensemble System Loaded");

// ==========================================================================
// BLOCKED PAGE - COUNTDOWN TIMER
// ==========================================================================
const BlockedPage = {
  timer: null,
  countdownElement: null,
  blockedUntil: null,

  init() {
    this.countdownElement = document.getElementById("countdownTimer");

    if (this.countdownElement) {
      const blockedUntilStr = this.countdownElement.getAttribute("data-until");

      if (blockedUntilStr) {
        // Parse datetime string (format: 2026-05-31 16:30:45.123456)
        this.blockedUntil = new Date(blockedUntilStr.replace(" ", "T"));
        this.startCountdown();
      }
    }
  },

  startCountdown() {
    this.updateCountdown();

    this.timer = setInterval(() => {
      this.updateCountdown();
    }, 1000);
  },

  updateCountdown() {
    const now = new Date();
    const diff = this.blockedUntil - now;

    if (diff <= 0) {
      clearInterval(this.timer);
      this.showUnblockMessage();

      setTimeout(() => {
        window.location.href = "/login";
      }, 2000);

      return;
    }

    const minutes = Math.floor(diff / 60000);
    const seconds = Math.floor((diff % 60000) / 1000);

    const minutesStr = String(minutes).padStart(2, "0");
    const secondsStr = String(seconds).padStart(2, "0");

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
        '<span style="color: #10b981;">✓ Model Ensemble Mengevaluasi Kembali: Akses Dibuka</span>';
    }
  },
};

// ==========================================================================
// DASHBOARD - AUTO REFRESH & STATS VIA REST API
// ==========================================================================
const Dashboard = {
  refreshInterval: 15000, // Diset ke 15 detik agar sinkronisasi data log ensemble berjalan cepat saat demo
  autoRefreshTimer: null,

  init() {
    console.log("Dashboard RF initialized");
    this.setupAutoRefresh();
    this.addTableInteractions();
  },

  setupAutoRefresh() {
    this.autoRefreshTimer = setInterval(() => {
      console.log("Auto-refreshing Random Forest dashboard...");
      this.refreshStats();
      this.refreshLogs();
    }, this.refreshInterval);
  },

  async refreshStats() {
    try {
      const welcomeText = document.querySelector(".welcome-text strong");
      if (!welcomeText) return;

      const username = welcomeText.textContent.trim();
      if (!username) return;

      const response = await fetch(`/api/stats/${username}`);
      const stats = await response.json();

      // Update stat card dinamis
      this.updateStatCard("total_attempts", stats.total_attempts);
      this.updateStatCard("failed_attempts", stats.failed_attempts);
      this.updateStatCard("successful_attempts", stats.successful_attempts);
      this.updateStatCard("current_state", stats.current_state);

      console.log("RF Stats refreshed:", stats);
    } catch (error) {
      console.error("Error refreshing stats:", error);
    }
  },

  updateStatCard(type, value) {
    const card = document.querySelector(`[data-stat="${type}"]`);
    if (card) {
      const valueElement = card.querySelector(".stat-value");
      if (valueElement) {
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

      const tbody = document.querySelector("table tbody");
      if (!tbody) return;

      tbody.innerHTML = "";

      logs.slice(0, 50).forEach((log) => {
        const row = this.createLogRow(log);
        tbody.appendChild(row);
      });

      console.log("RF Activity Logs refreshed");
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
      <td><strong>${this.escapeHtml(log.username)}</strong></td>
      <td class="${statusClass}">${statusText}</td>
      <td><code style="font-size: 11px">${this.escapeHtml(log.ip_address)}</code></td>
      <td><span class="state-label ${stateClass}">${this.escapeHtml(log.state)}</span></td>
      <td style="max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${this.escapeHtml(log.message)}</td>
      <td style="font-size: 11px; white-space: nowrap;">${this.formatTimestamp(log.timestamp)}</td>
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
    const rows = document.querySelectorAll("table tbody tr");
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

// ==========================================================================
// LOGIN PAGE - STATE ANIMATION
// ==========================================================================
const LoginStateAnimation = {
  init() {
    console.log("Login state animation initialized");

    const activeBadge = document.querySelector(".state-badge.active");
    if (activeBadge) {
      setTimeout(() => {
        activeBadge.style.animation =
          "popIn 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55)";
      }, 300);
    }

    this.setupFormAnimation();
  },

  setupFormAnimation() {
    const form = document.querySelector("form");
    if (!form) return;

    form.addEventListener("submit", () => {
      const button = form.querySelector(".btn-login");
      if (button) {
        button.innerHTML =
          '<span>Mengevaluasi Vektor Fitur...</span><span class="btn-icon">⏳</span>';
        button.disabled = true;
      }
    });
  },
};

// ==========================================================================
// INITIALIZATION ON PAGE LOAD
// ==========================================================================
document.addEventListener("DOMContentLoaded", () => {
  console.log("Page loaded, initializing components...");

  if (document.getElementById("countdownTimer")) {
    BlockedPage.init();
  }

  if (document.querySelector(".dashboard-container")) {
    Dashboard.init();
  }

  if (document.querySelector("form")) {
    LoginStateAnimation.init();
  }

  document
    .querySelectorAll("button, .btn-login, .btn-logout, .btn-back")
    .forEach((button) => {
      button.style.transition = "all 0.3s ease";
    });

  console.log("All Random Forest components initialized successfully");
});

// ==========================================================================
// CLEANUP ON PAGE UNLOAD
// ==========================================================================
window.addEventListener("beforeunload", () => {
  if (Dashboard.autoRefreshTimer) {
    clearInterval(Dashboard.autoRefreshTimer);
  }

  if (BlockedPage.timer) {
    clearInterval(BlockedPage.timer);
  }
});
