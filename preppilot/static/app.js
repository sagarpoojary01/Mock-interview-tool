const $ = (id) => document.getElementById(id);
let token = localStorage.getItem("token");
let registering = false;

async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers.Authorization = "Bearer " + token;
  const res = await fetch(path, { ...options, headers });
  if (res.status === 401 && token) { logout(); throw new Error("Session expired, please log in again"); }
  if (res.status === 204) return null;
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = Array.isArray(data.detail) ? data.detail.map((d) => d.msg).join(", ") : data.detail;
    throw new Error(detail || "Request failed");
  }
  return data;
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function showApp(loggedIn) {
  $("auth-view").hidden = loggedIn;
  $("app-view").hidden = !loggedIn;
  $("nav").hidden = !loggedIn;
  if (loggedIn) loadHistory();
}

function logout() {
  token = null;
  localStorage.removeItem("token");
  $("interview").hidden = true;
  showApp(false);
}

$("toggle-auth").onclick = (e) => {
  e.preventDefault();
  registering = !registering;
  $("full_name").hidden = !registering;
  $("full_name").required = registering;
  $("auth-title").textContent = registering ? "Register" : "Log in";
  $("toggle-auth").textContent = registering ? "Have an account? Log in" : "Need an account? Register";
};

$("auth-form").onsubmit = async (e) => {
  e.preventDefault();
  $("auth-error").textContent = "";
  const body = { email: $("email").value, password: $("password").value };
  if (registering) body.full_name = $("full_name").value;
  try {
    const data = await api(registering ? "/api/auth/register" : "/api/auth/login", { method: "POST", body: JSON.stringify(body) });
    token = data.access_token;
    localStorage.setItem("token", token);
    $("who").textContent = body.email;
    showApp(true);
  } catch (err) { $("auth-error").textContent = err.message; }
};

$("logout").onclick = logout;

$("new-form").onsubmit = async (e) => {
  e.preventDefault();
  $("new-error").textContent = "";
  $("start-btn").disabled = true;
  try {
    const session = await api("/api/sessions", {
      method: "POST",
      body: JSON.stringify({ role: $("role").value, level: $("level").value, num_questions: Number($("num").value) }),
    });
    renderSession(session);
    loadHistory();
  } catch (err) { $("new-error").textContent = err.message; }
  $("start-btn").disabled = false;
};

function renderSession(s) {
  const box = $("interview");
  box.hidden = false;
  box.innerHTML = `<h2>${escapeHtml(s.role)} (${escapeHtml(s.level)})</h2>` + s.questions.map((q, i) => `
    <div class="q" data-id="${q.id}">
      <p>${i + 1}. ${escapeHtml(q.text)}</p>
      <textarea placeholder="Type your answer..." ${q.answer ? "" : ""}>${escapeHtml(q.answer || "")}</textarea>
      <button data-session="${s.id}" data-q="${q.id}">${q.answer ? "Re-submit" : "Submit answer"}</button>
      <div class="result">${q.score ? resultHtml(q.score, q.feedback) : ""}</div>
    </div>`).join("");
  box.querySelectorAll("button[data-q]").forEach((btn) => {
    btn.onclick = async () => {
      const wrap = btn.closest(".q");
      const answer = wrap.querySelector("textarea").value.trim();
      if (!answer) return;
      btn.disabled = true;
      try {
        const q = await api(`/api/sessions/${btn.dataset.session}/questions/${btn.dataset.q}/answer`, { method: "POST", body: JSON.stringify({ answer }) });
        wrap.querySelector(".result").innerHTML = resultHtml(q.score, q.feedback);
        loadHistory();
      } catch (err) { wrap.querySelector(".result").innerHTML = `<p class="error">${escapeHtml(err.message)}</p>`; }
      btn.disabled = false;
    };
  });
  box.scrollIntoView({ behavior: "smooth" });
}

function resultHtml(score, feedback) {
  return `<span class="score">${score}/10</span><p class="feedback">${escapeHtml(feedback)}</p>`;
}

async function loadHistory() {
  try {
    const rows = await api("/api/sessions");
    $("history").innerHTML = rows.length ? rows.map((r) => `
      <li>
        <span>${escapeHtml(r.role)} (${escapeHtml(r.level)}) &middot; ${r.answered}/${r.total} answered &middot; avg ${r.average_score ?? "-"}</span>
        <span><button class="ghost" data-open="${r.id}">Open</button> <button class="ghost" data-del="${r.id}">Delete</button></span>
      </li>`).join("") : '<li class="muted">No sessions yet.</li>';
    document.querySelectorAll("[data-open]").forEach((b) => (b.onclick = async () => renderSession(await api("/api/sessions/" + b.dataset.open))));
    document.querySelectorAll("[data-del]").forEach((b) => (b.onclick = async () => {
      await api("/api/sessions/" + b.dataset.del, { method: "DELETE" });
      $("interview").hidden = true;
      loadHistory();
    }));
  } catch (_) { /* handled by api() */ }
}

showApp(Boolean(token));
