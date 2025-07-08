const form      = document.getElementById("chat-form");
const textbox   = document.getElementById("textbox");
const messages  = document.getElementById("messages");
const micButton = document.getElementById("mic");

/* ---------- Helpers ------------------------------------- */
function addMessage(text, cls) {
  const div = document.createElement("div");
  div.className = `message ${cls}`;
  div.textContent = text;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

function speak(text) {
  const utter = new SpeechSynthesisUtterance(text);
  speechSynthesis.speak(utter);
}

async function sendToServer(message) {
  // add typing dots
  const typing = document.importNode(
    document.getElementById("typing-template").content, true
  );
  messages.appendChild(typing);
  messages.scrollTop = messages.scrollHeight;

  // send
  const res = await fetch("/api/chat", {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify({ message })
  });

  const data = await res.json();
  messages.querySelector(".typing")?.remove();

  if (!res.ok) throw new Error(data.error || "Server error");
  return data.reply;
}

/* ---------- 🕒 Local time helper ------------------------- */
function localTimeSentence() {
  const now = new Date();
  return `It's ${now.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}.`;
}
const TIME_REGEX = /what\s+time|time\s+is\s+it|current\s+time|tell\s+me\s+the\s+time/i;

/* ---------- Submit handler ------------------------------- */
form.addEventListener("submit", async e => {
  e.preventDefault();
  const userText = textbox.value.trim();
  if (!userText) return;

  addMessage(userText, "user");
  textbox.value = "";
  form.querySelector("button[type='submit']").disabled = true;

  /* —— Local “what time” interception —— */
  if (TIME_REGEX.test(userText)) {
    const reply = localTimeSentence();
    addMessage(reply, "bot");
    speak(reply);
    form.querySelector("button[type='submit']").disabled = false;
    textbox.focus();
    return;                          // skip backend
  }

  /* —— Otherwise hit the backend —— */
  try {
    const reply = await sendToServer(userText);
    addMessage(reply, "bot");
    speak(reply);
  } catch (err) {
    addMessage("Error: " + err.message, "bot");
  } finally {
    form.querySelector("button[type='submit']").disabled = false;
    textbox.focus();
  }
});

/* ---------- Speech Recognition --------------------------- */
let recognizer;
if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;
  recognizer = new SpeechRecognition();
  recognizer.lang = "en-US";
  recognizer.interimResults = false;
  recognizer.continuous = false;

  micButton.addEventListener("mousedown", () => {
    recognizer.start();
    micButton.innerHTML = '<i data-lucide="square"></i>';
    lucide.createIcons();
  });

  recognizer.addEventListener("result", e => {
    const transcript = e.results[0][0].transcript;
    textbox.value = transcript;
    form.requestSubmit();
  });

  recognizer.addEventListener("end", () => {
    micButton.innerHTML = '<i data-lucide="mic"></i>';
    lucide.createIcons();
  });
} else {
  micButton.disabled = true;
  micButton.title = "Speech Recognition not supported";
}

/* ---------- Theme toggle --------------------------------- */
const themeToggle = document.getElementById("theme-toggle");
const systemDark  = window.matchMedia("(prefers-color-scheme: dark)");

themeToggle.onclick = () => {
  const dark = !(document.documentElement.dataset.theme === "dark");
  setTheme(dark ? "dark" : "light");
};

function setTheme(name) {
  document.documentElement.dataset.theme = name;
  localStorage.setItem("theme", name);
}

function initTheme() {
  const saved = localStorage.getItem("theme");
  if (saved)      setTheme(saved);
  else if (systemDark.matches) setTheme("dark");
}
initTheme();