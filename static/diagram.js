let diagramData = { problem: null, whys: [], rootcause: null };

function parseAndUpdateDiagram(text) {
  const lines = text.split('\n');
  for (const line of lines) {
    const clean = line.replace(/\*\*/g, "").trim();
    if (clean.startsWith("PROBLEM:")) {
      diagramData = { problem: null, whys: [], rootcause: null };
      diagramData.problem = clean.replace("PROBLEM:", "").trim();
      document.getElementById("export-btn").style.display = "none";
    } else if (/^WHY([1-9]|10):/.test(clean)) {
      const num = parseInt(clean.match(/^WHY(\d+):/)[1]);
      const answer = clean.replace(/^WHY\d+:/, "").trim();
      diagramData.whys[num - 1] = answer;
    } else if (clean.startsWith("ROOT CAUSE:")) {
      diagramData.rootcause = clean.replace("ROOT CAUSE:", "").trim();
    }
  }
  renderDiagram();
  if (diagramData.rootcause) {
    document.getElementById("export-btn").style.display = "block";
  }
}

function renderDiagram() {
  const content = document.getElementById("diagram-content");
  if (!diagramData.problem && diagramData.whys.length === 0) return;

  content.innerHTML = "";
  const STEP = 32;

  if (diagramData.problem) {
    const node = document.createElement("div");
    node.className = "diagram-problem";
    node.textContent = "Problem: " + diagramData.problem;
    content.appendChild(node);
  }

  diagramData.whys.forEach((why, i) => {
    if (!why) return;
    const row = document.createElement("div");
    row.className = "diagram-node";
    row.style.marginLeft = ((i + 1) * STEP) + "px";
    row.innerHTML = `<div class="diagram-why">Why?</div><div class="diagram-answer">${why}</div>`;
    content.appendChild(row);
  });

  if (diagramData.rootcause) {
    const node = document.createElement("div");
    node.className = "diagram-rootcause";
    node.textContent = "Root cause: " + diagramData.rootcause;
    content.appendChild(node);
  }
}
