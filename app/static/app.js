const API = "";

let TG_ID = null;
let TG_INIT_DATA = null;

document.addEventListener("DOMContentLoaded", () => {

  const balanceEl = document.getElementById("balance");
  const energyEl = document.getElementById("energy");
  const maxEnergyEl = document.getElementById("max-energy");
  const energyFill = document.getElementById("energy-fill");
  const coin = document.getElementById("coin");
  const levelTitle = document.getElementById("level-title");
  const levelPercent = document.getElementById("level-percent");
  const levelFill = document.getElementById("level-fill");
  const levelRemaining = document.getElementById("level-remaining");


  // ===== Wait for Telegram WebApp =====
  async function waitForTelegram(timeout = 3000) {
    return new Promise((resolve) => {
      const start = Date.now();

      const check = () => {
        if (window.Telegram && Telegram.WebApp) {
          resolve(true);
        } else if (Date.now() - start > timeout) {
          resolve(false);
        } else {
          setTimeout(check, 100);
        }
      };

      check();
    });
  }

  // ===== Get Telegram User (Safe) =====
  function getTelegramUser() {
    if (!window.Telegram || !Telegram.WebApp) return null;

    const webApp = Telegram.WebApp;

    // Preferred
    if (webApp.initDataUnsafe?.user?.id) {
      return webApp.initDataUnsafe.user;
    }

    // Fallback (desktop cases)
    if (webApp.initData) {
      try {
        const params = new URLSearchParams(webApp.initData);
        const userStr = params.get("user");
        if (userStr) return JSON.parse(userStr);
      } catch (e) {
        console.error("Fallback parse error", e);
      }
    }

    return null;
  }

  function showNotTelegram() {
    document.body.innerHTML = `
      <div style="text-align:center;margin-top:60px">
        <h2>Open inside Telegram</h2>
        <p>t.me/RanjbarCoinBot</p>
      </div>
    `;
  }

  // ===== Init Telegram =====
  async function initTelegram() {
    const exists = await waitForTelegram();
    if (!exists) {
      showNotTelegram();
      return false;
    }

    const webApp = Telegram.WebApp;
    webApp.ready();

    const user = getTelegramUser();
    if (!user) {
      showNotTelegram();
      return false;
    }

    TG_ID = user.id;
    TG_INIT_DATA = webApp.initData; // برای verify سمت سرور

    console.log("Telegram ID:", TG_ID);
    return true;
  }

  // ===== Update UI =====
  function updateUI(data) {
    balanceEl.innerText = data.balance;
    energyEl.innerText = data.energy;
    maxEnergyEl.innerText = data.max_energy;

    const percent = (data.energy / data.max_energy) * 100;
    energyFill.style.width = percent + "%";

    coin.style.pointerEvents = data.energy > 0 ? "auto" : "none";
    coin.style.opacity = data.energy > 0 ? "1" : "0.5";
    // LEVEL
    if (data.level) {
      levelTitle.innerText = data.level;
      levelPercent.innerText = data.level_percent + "%";
      levelFill.style.width = data.level_percent + "%";
    
      if (data.level_remaining > 0) {
        levelRemaining.innerText =
          data.level_remaining.toLocaleString() + " سکه تا سطح بعدی";
      } else {
        levelRemaining.innerText = "شما به بالاترین سطح رسیدید 👑";
      }
    }

  }

  // ===== API Request Wrapper =====
  async function apiPost(endpoint) {
    const res = await fetch(API + endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: TG_ID,
        init_data: TG_INIT_DATA  // 🔐 آماده برای verify آینده
      })
    });

    const data = await res.json();
    if (!res.ok) throw data;
    return data;
  }

  // ===== Load State =====
  async function loadState() {
    try {
      const data = await apiPost("/state");
      updateUI(data);
    } catch (e) {
      console.error("Load state error", e);
    }
  }

  // ===== Mine =====
  async function tap() {
    try {
      const data = await apiPost("/mine");

      const mineAmount = data.mine_power || 1;
      updateUI(data);

      const plusEl = document.createElement("div");
      plusEl.classList.add("floating-plus");
      plusEl.innerText = "+" + mineAmount;

      const rect = coin.getBoundingClientRect();
      plusEl.style.left = rect.width / 2 - 10 + "px";
      plusEl.style.bottom = rect.height + "px";

      coin.appendChild(plusEl);
      setTimeout(() => plusEl.remove(), 800);

    } catch (err) {
      console.error("Mine error:", err);
    }
  }

  // ===== Start App =====
  (async () => {
    const ok = await initTelegram();
    if (!ok) return;

    coin.addEventListener("click", tap);
    loadState();
    setInterval(loadState, 5000);
  })();

});
