/**
 * GameVault — Review and Rating System
 *
 * Interactive star rating, AJAX review submission, and dynamic review list updates.
 */
(function () {
  "use strict";

  // ─── Star Rating Widget ─────────────────────────────────────────────────────

  /**
   * Initialize an interactive clickable star rating widget.
   * The widget replaces the hidden rating input and radio buttons with
   * clickable star spans that visually update on hover and click.
   */
  function initStarRating() {
    const starInput = document.getElementById("starInput");
    if (!starInput) return;

    const ratingInput = starInput.querySelector('input[name="rating"]');
    if (!ratingInput) return;

    // Get all star labels (the <label> elements with star-label class)
    const starLabels = starInput.querySelectorAll(".star-label");
    if (starLabels.length === 0) return;

    // Read current value from checked radio
    let currentRating = parseInt(
      starInput.querySelector('input[name="rating"]:checked')?.value || 0
    );
    let hoverRating = 0;

    // Helper: update visual state
    function setStars(rating) {
      starLabels.forEach(function (label) {
        const val = parseInt(label.getAttribute("for").replace("star", ""));
        const isActive = val <= rating;
        label.classList.toggle("active", isActive);
      });
    }

    // Click handler
    starLabels.forEach(function (label) {
      label.addEventListener("click", function (e) {
        e.preventDefault();
        const val = parseInt(label.getAttribute("for").replace("star", ""));
        currentRating = val;
        hoverRating = 0;

        // Update the hidden radio
        const radio = document.getElementById("star" + val);
        if (radio) radio.checked = true;

        setStars(val);
      });
    });

    // Hover handlers
    starInput.addEventListener("mouseenter", function () {
      hoverRating = currentRating;
    });

    starInput.addEventListener("mouseleave", function () {
      hoverRating = 0;
      setStars(currentRating);
    });

    // We attach hover to individual labels
    starLabels.forEach(function (label) {
      label.addEventListener("mouseenter", function () {
        const val = parseInt(label.getAttribute("for").replace("star", ""));
        setStars(val);
      });
    });

    // Initial state
    setStars(currentRating);
  }

  // ─── AJAX Review Submission ─────────────────────────────────────────────────

  /**
   * Submit a review via AJAX (fetch) and dynamically update the review list.
   * @param {Event} e - The form submit event
   */
  async function submitReview(e) {
    e.preventDefault();

    const form = e.currentTarget;
    const feedback = document.getElementById("reviewFeedback");
    const submitBtn = form.querySelector('button[type="submit"]');
    const ratingEl = form.querySelector('input[name="rating"]:checked');
    const rating = ratingEl ? parseInt(ratingEl.value) : 0;
    const body = document.getElementById("reviewBody")?.value || "";
    const igdbId = form.dataset.igdbId;

    if (!rating) {
      showFeedback(feedback, "Please select a rating.", "error");
      return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = "Submitting...";
    clearFeedback(feedback);

    try {
      const response = await fetch("/api/reviews", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          igdb_id: parseInt(igdbId),
          rating: rating,
          body: body,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        showFeedback(feedback, "Review submitted! Updating...", "success");
        // Reset form
        form.reset();
        if (ratingEl) ratingEl.checked = true; // re-check default
        initStarRating(); // re-sync stars

        // Dynamically fetch and render updated reviews
        await refreshReviews(igdbId);
      } else {
        showFeedback(
          feedback,
          data.error || "Failed to submit review.",
          "error"
        );
        submitBtn.disabled = false;
        submitBtn.textContent = "Submit Review";
      }
    } catch (err) {
      showFeedback(feedback, "Network error. Please try again.", "error");
      submitBtn.disabled = false;
      submitBtn.textContent = "Submit Review";
    }
  }

  // ─── Dynamic Review List Update ─────────────────────────────────────────────

  /**
   * Fetch reviews for a game and re-render the review list in the DOM.
   * @param {number|string} igdbId - The IGDB game ID
   */
  async function refreshReviews(igdbId) {
    const reviewsList = document.getElementById("reviewsList");
    if (!reviewsList) return;

    try {
      const response = await fetch("/api/reviews/" + igdbId);
      if (!response.ok) return;

      const reviews = await response.json();
      renderReviews(reviewsList, reviews);
    } catch (err) {
      // Silently fail — page still works with server-side render
    }
  }

  /**
   * Render reviews into the reviews container.
   * @param {HTMLElement} container - The reviews list element
   * @param {Array} reviews - Array of review objects
   */
  function renderReviews(container, reviews) {
    if (!reviews || reviews.length === 0) {
      container.innerHTML =
        '<div class="empty-state"><p>No reviews yet for this game.</p></div>';
      return;
    }

    var html = "";
    for (var i = 0; i < reviews.length; i++) {
      var r = reviews[i];
      var starsHtml = "";
      for (var s = 0; s < 5; s++) {
        starsHtml +=
          '<span class="star' + (s < r.rating ? " filled" : "") + '">&#9733;</span>';
      }

      var dateStr = "";
      if (r.created_at) {
        var d = new Date(r.created_at);
        dateStr = d.toLocaleDateString("en-US", {
          year: "numeric",
          month: "short",
          day: "numeric",
        });
      }

      var bodyHtml = "";
      if (r.body) {
        bodyHtml =
          '<p class="review-card-body">' +
          escapeHtml(r.body) +
          "</p>";
      }

      html +=
        '<div class="review-card card">' +
        '<div class="review-card-header">' +
        '<a href="/profile/' +
        encodeURIComponent(r.username) +
        '" class="review-author">' +
        escapeHtml(r.username) +
        "</a>" +
        '<span class="review-date">' +
        dateStr +
        "</span>" +
        "</div>" +
        '<div class="review-card-rating">' +
        '<span class="stars">' +
        starsHtml +
        "</span>" +
        '<span class="rating-value">' +
        r.rating +
        "/5</span>" +
        "</div>" +
        bodyHtml +
        "</div>";
    }

    container.innerHTML = html;
  }

  // ─── Helpers ────────────────────────────────────────────────────────────────

  function showFeedback(el, message, type) {
    if (!el) return;
    el.textContent = message;
    el.className = "review-feedback " + type;
    el.style.display = "block";
  }

  function clearFeedback(el) {
    if (!el) return;
    el.className = "review-feedback";
    el.style.display = "none";
  }

  function escapeHtml(str) {
    if (!str) return "";
    var div = document.createElement("div");
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
  }

  // ─── Init ───────────────────────────────────────────────────────────────────

  document.addEventListener("DOMContentLoaded", function () {
    initStarRating();

    var form = document.getElementById("reviewForm");
    if (form) {
      form.addEventListener("submit", submitReview);
    }
  });
})();
