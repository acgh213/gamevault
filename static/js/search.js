/**
 * GameVault Search Autocomplete
 *
 * Debounced search input that fetches results from /api/search?q=
 * and displays an autocomplete dropdown with game cover thumbnails.
 */
(function () {
  "use strict";

  const SEARCH_INPUT_SELECTOR = ".search-input";
  const AUTOCOMPLETE_CONTAINER_ID = "search-autocomplete";
  const MIN_QUERY_LENGTH = 2;
  const DEBOUNCE_MS = 300;

  const searchInput = document.querySelector(SEARCH_INPUT_SELECTOR);
  if (!searchInput) return;

  // Create autocomplete dropdown container
  const autocomplete = document.createElement("div");
  autocomplete.id = AUTOCOMPLETE_CONTAINER_ID;
  autocomplete.className = "autocomplete-dropdown";
  autocomplete.style.display = "none";
  searchInput.parentNode.insertBefore(autocomplete, searchInput.nextSibling);

  // --- Debounce utility ---
  let debounceTimer = null;

  function debounce(fn, delay) {
    return function () {
      const args = arguments;
      const ctx = this;
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(function () {
        fn.apply(ctx, args);
      }, delay);
    };
  }

  // --- Fetch results ---
  function fetchResults(query) {
    if (query.length < MIN_QUERY_LENGTH) {
      hideAutocomplete();
      return;
    }

    fetch("/api/search?q=" + encodeURIComponent(query))
      .then(function (response) {
        if (!response.ok) {
          throw new Error("Search request failed");
        }
        return response.json();
      })
      .then(function (data) {
        renderResults(data);
      })
      .catch(function () {
        hideAutocomplete();
      });
  }

  // --- Render dropdown ---
  function renderResults(games) {
    if (!games || games.length === 0) {
      hideAutocomplete();
      return;
    }

    autocomplete.innerHTML = "";
    autocomplete.style.display = "block";

    games.forEach(function (game) {
      var item = document.createElement("a");
      item.className = "autocomplete-item";
      item.href = "/game/" + game.id;

      // Cover thumbnail
      var thumb = document.createElement("img");
      thumb.className = "autocomplete-thumb";
      if (game.cover_url) {
        // Use small thumbnails for the dropdown
        var thumbUrl = game.cover_url.replace("t_cover_big", "t_thumb");
        thumb.src = thumbUrl;
        thumb.alt = game.name;
      } else {
        thumb.alt = "";
        thumb.style.display = "none";
      }

      // Game name
      var nameSpan = document.createElement("span");
      nameSpan.className = "autocomplete-name";
      nameSpan.textContent = game.name;

      // Year if available
      if (game.release_date) {
        var yearSpan = document.createElement("span");
        yearSpan.className = "autocomplete-year";
        var year = game.release_date.slice(-4);
        yearSpan.textContent = year;
        item.appendChild(thumb);
        item.appendChild(nameSpan);
        item.appendChild(yearSpan);
      } else {
        item.appendChild(thumb);
        item.appendChild(nameSpan);
      }

      item.addEventListener("click", function (e) {
        hideAutocomplete();
      });

      autocomplete.appendChild(item);
    });
  }

  // --- Hide dropdown ---
  function hideAutocomplete() {
    autocomplete.style.display = "none";
    autocomplete.innerHTML = "";
  }

  // --- Debounced input handler ---
  var debouncedFetch = debounce(function () {
    var query = searchInput.value.trim();
    fetchResults(query);
  }, DEBOUNCE_MS);

  searchInput.addEventListener("input", debouncedFetch);

  // --- Close on Escape ---
  searchInput.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      hideAutocomplete();
    }
  });

  // --- Close on click outside ---
  document.addEventListener("click", function (e) {
    var target = e.target;
    if (
      target !== autocomplete &&
      !autocomplete.contains(target) &&
      target !== searchInput
    ) {
      hideAutocomplete();
    }
  });
})();
