/**
 * GameVault — Lists and Shelves JavaScript
 * Handles create list modal, add-to-list dropdown, remove-from-list.
 */

(function () {
  "use strict";

  // ─── Create List Modal ────────────────────────────────────────────────────

  const modal = document.getElementById("createListModal");
  const openBtns = document.querySelectorAll("#createListBtn, #emptyCreateBtn");
  const closeBtns = document.querySelectorAll(
    "#closeModalBtn, #cancelModalBtn"
  );
  const form = document.getElementById("createListForm");
  const feedback = document.getElementById("listFeedback");

  function openModal() {
    if (modal) modal.style.display = "flex";
    if (feedback) {
      feedback.textContent = "";
      feedback.className = "review-feedback";
    }
    if (form) form.reset();
  }

  function closeModal() {
    if (modal) modal.style.display = "none";
  }

  openBtns.forEach((btn) => btn && btn.addEventListener("click", openModal));

  closeBtns.forEach((btn) =>
    btn && btn.addEventListener("click", closeModal)
  );

  if (modal) {
    modal.addEventListener("click", function (e) {
      if (e.target === modal) closeModal();
    });
  }

  if (form) {
    form.addEventListener("submit", async function (e) {
      e.preventDefault();
      const name = document.getElementById("listName").value.trim();
      const description = document
        .getElementById("listDescription")
        .value.trim();
      const submitBtn = form.querySelector('button[type="submit"]');

      if (!name) return;

      submitBtn.disabled = true;
      submitBtn.textContent = "Creating...";
      if (feedback) {
        feedback.className = "review-feedback";
        feedback.textContent = "";
      }

      try {
        const response = await fetch("/api/lists", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name, description }),
        });
        const data = await response.json();

        if (response.ok) {
          if (feedback) {
            feedback.className = "review-feedback success";
            feedback.textContent = "List created! Refreshing...";
          }
          setTimeout(() => location.reload(), 800);
        } else {
          if (feedback) {
            feedback.className = "review-feedback error";
            feedback.textContent = data.error || "Failed to create list.";
          }
          submitBtn.disabled = false;
          submitBtn.textContent = "Create List";
        }
      } catch (err) {
        if (feedback) {
          feedback.className = "review-feedback error";
          feedback.textContent = "Network error. Please try again.";
        }
        submitBtn.disabled = false;
        submitBtn.textContent = "Create List";
      }
    });
  }

  // ─── Add to List Dropdown (on game pages) ─────────────────────────────────

  const addToListBtn = document.getElementById("addToListBtn");
  const addToListDropdown = document.getElementById("addToListDropdown");
  const listsContainer = document.getElementById("listsContainer");

  if (addToListBtn && addToListDropdown) {
    addToListBtn.addEventListener("click", function () {
      const isVisible = addToListDropdown.style.display === "block";
      addToListDropdown.style.display = isVisible ? "none" : "block";
    });

    // Close dropdown on click outside
    document.addEventListener("click", function (e) {
      if (
        addToListDropdown.style.display === "block" &&
        !addToListBtn.contains(e.target) &&
        !addToListDropdown.contains(e.target)
      ) {
        addToListDropdown.style.display = "none";
      }
    });
  }

  // Fetch user's lists and populate dropdown
  if (addToListDropdown && listsContainer) {
    const igdbId = addToListDropdown.dataset.igdbId;
    const gameId = addToListDropdown.dataset.gameId;

    // We'll use the existing lists data if available, otherwise fetch
    // Lists data is embedded in data-lists attribute by the template
    try {
      const listsData = JSON.parse(addToListDropdown.dataset.lists || "[]");
      renderListsDropdown(listsData, igdbId, gameId);
    } catch (e) {
      // Lists will be empty, dropdown shows nothing useful
    }
  }

  function renderListsDropdown(lists, igdbId, gameId) {
    if (!lists || lists.length === 0) {
      listsContainer.innerHTML =
        '<div class="dropdown-empty">No lists yet. <a href="/lists">Create one</a>.</div>';
      return;
    }

    listsContainer.innerHTML = lists
      .map(
        (list) => `
      <div class="dropdown-item" data-list-id="${list.id}" data-game-id="${gameId}">
        <span class="dropdown-item-name">${escapeHtml(list.name)}</span>
        <span class="dropdown-item-count">${list.game_ids ? list.game_ids.length : 0}</span>
      </div>
    `
      )
      .join("");

    listsContainer.querySelectorAll(".dropdown-item").forEach((item) => {
      item.addEventListener("click", async function () {
        const listId = this.dataset.listId;
        const gId = this.dataset.gameId;
        if (!gId) return;

        this.classList.add("loading");

        try {
          const response = await fetch(`/api/lists/${listId}/games`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ game_id: parseInt(gId) }),
          });
          const data = await response.json();

          if (response.ok) {
            this.classList.add("added");
            this.innerHTML = `<span class="dropdown-item-name">&#10003; ${escapeHtml(list.name)}</span>`;
            showToast(`Added to "${list.name}"`, "success");
          } else {
            showToast(data.error || "Failed to add", "error");
            this.classList.remove("loading");
          }
        } catch (err) {
          showToast("Network error", "error");
          this.classList.remove("loading");
        }
      });
    });
  }

  // ─── Remove from List (on lists page) ─────────────────────────────────────

  document.querySelectorAll("[data-remove-game]").forEach((btn) => {
    btn.addEventListener("click", async function () {
      const listId = this.dataset.listId;
      const gameId = this.dataset.gameId;
      const gameName = this.dataset.gameName || "Game";

      if (!confirm(`Remove "${gameName}" from this list?`)) return;

      this.disabled = true;
      this.textContent = "Removing...";

      try {
        const response = await fetch(`/api/lists/${listId}/games/${gameId}`, {
          method: "DELETE",
        });
        const data = await response.json();

        if (response.ok) {
          // Remove the game card from the DOM
          const gameCard = this.closest("[data-game-card]");
          if (gameCard) {
            gameCard.remove();
          } else {
            location.reload();
          }
          showToast(data.message || "Removed from list", "success");
        } else {
          showToast(data.error || "Failed to remove", "error");
          this.disabled = false;
          this.textContent = "Remove";
        }
      } catch (err) {
        showToast("Network error", "error");
        this.disabled = false;
        this.textContent = "Remove";
      }
    });
  });

  // ─── Helpers ──────────────────────────────────────────────────────────────

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }

  function showToast(message, type) {
    const toast = document.createElement("div");
    toast.className = `toast toast-${type || "info"}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    requestAnimationFrame(() => {
      toast.classList.add("toast-visible");
    });

    setTimeout(() => {
      toast.classList.remove("toast-visible");
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }
})();
