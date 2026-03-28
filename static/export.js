async function exportPDF() {
  if (!diagramData.rootcause) return;
  const btn = document.getElementById("export-btn");
  btn.textContent = "⏳ Generiram...";
  btn.disabled = true;
  try {
    const response = await fetch("/export-pdf", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ diagram: diagramData })
    });
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "5why-analiza.pdf";
    a.click();
    URL.revokeObjectURL(url);
  } catch (err) {
    alert("Napaka pri izvozu: " + err.message);
  }
  btn.textContent = "⬇ Izvozi PDF";
  btn.disabled = false;
}
