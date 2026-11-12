// ---- Configuration -------------------------------------------------------
const PRODUCTION_API_URL = "https://ai-code-review-assistant-1-7ctp.onrender.com";
const isLocal = ["localhost", "127.0.0.1", ""].includes(window.location.hostname);
const API_BASE_URL = isLocal ? "http://localhost:8000" : PRODUCTION_API_URL;
const REQUEST_TIMEOUT_MS = 60000; // free-tier Render can take ~30-50s to wake up

const reviewBtn = document.getElementById("reviewBtn");
const result = document.getElementById("result");

// ---- Rendering (DOM APIs only; never innerHTML with model output) --------
function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
}

function showMessage(text, isError = false) {
    result.replaceChildren(el("p", isError ? "msg error" : "msg", text));
}

function renderSection(title, items) {
    const section = el("div", "review-section");
    section.appendChild(el("h3", null, title));

    if (!items.length) {
        section.appendChild(el("p", "empty", "Nothing to report."));
        return section;
    }

    const list = el("ul");
    items.forEach((item) => {
        const text = typeof item === "string" ? item : item.description;
        const li = el("li");
        if (item.line) li.appendChild(el("span", "line-tag", "Line " + item.line));
        li.appendChild(document.createTextNode(text));
        list.appendChild(li);
    });
    section.appendChild(list);
    return section;
}

function renderReview(data) {
    const review = data.review;
    const frag = document.createDocumentFragment();

    const header = el("div", "review-header");
    header.appendChild(el("span", "rating", "\u2B50 " + review.rating + "/10"));
    if (data.cached) header.appendChild(el("span", "cached-tag", "cached"));
    frag.appendChild(header);
    frag.appendChild(el("p", "summary", review.summary));

    frag.appendChild(renderSection("\uD83D\uDC1E Bugs", review.bugs));
    frag.appendChild(renderSection("\u26A1 Optimizations", review.optimizations));
    frag.appendChild(renderSection("\uD83E\uDDF9 Best Practices", review.best_practices));
    frag.appendChild(renderSection("\uD83D\uDCA1 Suggestions", review.suggestions));

    result.replaceChildren(frag);
}

// ---- Error messages ------------------------------------------------------
function errorMessageFor(status, body) {
    if (status === 422) return "Invalid input. Code must be non-empty and under 10,000 characters.";
    if (status === 429) return "Too many requests. Please wait a minute and try again.";
    if (status === 502 || status === 503) {
        return (body && body.detail) || "The AI service is unavailable. Please try again.";
    }
    return "Something went wrong (error " + status + ").";
}

// ---- Main handler --------------------------------------------------------
reviewBtn.addEventListener("click", async function () {
    const language = document.getElementById("language").value;
    const code = document.getElementById("code").value;

    if (code.trim() === "") {
        showMessage("Please enter some code to review.", true);
        return;
    }

    reviewBtn.disabled = true;
    showMessage("Reviewing your code... (the first request may take up to a minute if the server is waking up)");

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

    try {
        const response = await fetch(API_BASE_URL + "/review", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ language: language, code: code }),
            signal: controller.signal,
        });

        let body = null;
        try { body = await response.json(); } catch (_) { /* non-JSON error page */ }

        if (!response.ok) {
            showMessage(errorMessageFor(response.status, body), true);
            return;
        }
        renderReview(body);
    } catch (error) {
        const timedOut = error.name === "AbortError";
        showMessage(
            timedOut
                ? "The request timed out. Please try again."
                : "Unable to connect to the backend. Please try again.",
            true
        );
        console.error(error);
    } finally {
        clearTimeout(timer);
        reviewBtn.disabled = false;
    }
});
