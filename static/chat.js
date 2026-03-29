const SESSION_ID = Date.now().toString();
let history = [];

document.getElementById("user-input").addEventListener("keydown", e => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

document.getElementById("user-input").addEventListener("input", function() {
  this.style.height = "auto";
  this.style.height = Math.min(this.scrollHeight, 120) + "px";
});

document.getElementById("pdf-input").addEventListener("change", function() {
  const label = document.getElementById("pdf-label");
  const badge = document.getElementById("pdf-badge");
  const input = document.getElementById("user-input");
  if (this.files[0]) {
    label.classList.add("active");
    badge.textContent = this.files[0].name;
    input.placeholder = "Kliknite Pošlji za avtomatsko 5WHY analizo ali vpišite lastno vprašanje...";
  } else {
    label.classList.remove("active");
    badge.textContent = "";
    input.placeholder = "Napišite sporočilo...";
  }
});

function addMessage(role, text) {
  const msgs = document.getElementById("messages");
  const welcome = msgs.querySelector(".welcome");
  if (welcome) welcome.remove();

  const div = document.createElement("div");
  div.className = `message ${role}`;

  const label = document.createElement("div");
  label.className = "message-label";
  label.textContent = role === "user" ? "Vi" : role === "error" ? "Napaka" : "Asistent";

  const bubble = document.createElement("div");
  bubble.className = "message-bubble";
  bubble.textContent = text;

  div.appendChild(label);
  div.appendChild(bubble);
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;

  if (role === "assistant") {
    parseAndUpdateDiagram(text);
  }
}

function showTyping() {
  const msgs = document.getElementById("messages");
  const el = document.createElement("div");
  el.className = "typing";
  el.id = "typing-indicator";
  el.innerHTML = "<span></span><span></span><span></span>";
  msgs.appendChild(el);
  msgs.scrollTop = msgs.scrollHeight;
}

function hideTyping() {
  const el = document.getElementById("typing-indicator");
  if (el) el.remove();
}

async function sendMessage() {
  const input = document.getElementById("user-input");
  const pdfInput = document.getElementById("pdf-input");
  const pdfFile = pdfInput.files[0];
  let text = input.value.trim();

  if (!text && !pdfFile) return;

  // Če je PDF naložen brez besedila, avtomatsko zahtevaj 5WHY analizo
  if (!text && pdfFile) {
    text = "Izvedi 5WHY analizo tega dokumenta.";
  }

  const btn = document.getElementById("send-btn");
  btn.disabled = true;
  input.value = "";
  input.style.height = "auto";

  const displayText = pdfFile ? `📄 ${pdfFile.name}\n\n${text}` : text;
  addMessage("user", displayText);
  history.push({ role: "user", content: text });
  showTyping();

  try {
    let response;

    if (pdfFile) {
      const formData = new FormData();
      formData.append("messages", JSON.stringify(history));
      formData.append("pdf", pdfFile);
      formData.append("session_id", SESSION_ID);
      response = await fetch("/chat", { method: "POST", body: formData });
      pdfInput.value = "";
      document.getElementById("pdf-label").classList.remove("active");
      document.getElementById("pdf-badge").textContent = "";
    } else {
      response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Session-ID": SESSION_ID },
        body: JSON.stringify({ messages: history })
      });
    }

    const data = await response.json();
    if (data.error) throw new Error(data.error);

    history.push({ role: "assistant", content: data.reply });
    hideTyping();
    addMessage("assistant", data.reply);

  } catch (err) {
    hideTyping();
    history.pop();
    addMessage("error", "Napaka: " + err.message);
  }

  btn.disabled = false;
  input.focus();
}

function clearChat() {
  history = [];
  diagramData = { problem: null, whys: [], rootcause: null };
  const msgs = document.getElementById("messages");
  msgs.innerHTML = '<div class="welcome">Pogovor počiščen. Napišite novo vprašanje.</div>';
  document.getElementById("diagram-content").innerHTML = '<div class="diagram-empty">Diagram se bo prikazal med analizo...</div>';
  document.getElementById("export-btn").style.display = "none";
}
