// The page reads data/bonuses.json. No casino figures are embedded in HTML/JS.
const status = document.getElementById("status");
const body = document.getElementById("casino-body");
const count = document.getElementById("count");
const tableWrap = document.getElementById("table-wrap");
const updated = document.getElementById("updated");

function cell(label, text, className = "") {
  const td = document.createElement("td");
  td.dataset.label = label;
  if (className) td.className = className;
  td.textContent = text;
  return td;
}

async function loadBonuses() {
  try {
    const response = await fetch("./data/bonuses.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    if (!Array.isArray(data.casinos) || data.casinos.length !== 3) {
      throw new Error("Run python scraper.py first to generate 3 real records.");
    }
    body.replaceChildren();
    for (const casino of data.casinos) {
      const tr = document.createElement("tr");
      const nameCell = cell("Casino", casino.name);
      nameCell.className = "casino-name";
      const symbol = document.createElement("span");
      symbol.className = "casino-symbol";
      symbol.setAttribute("aria-hidden", "true");
      symbol.textContent = "♛";
      nameCell.prepend(symbol);
      tr.appendChild(nameCell);
      tr.appendChild(cell("Welcome bonus", casino.welcome_bonus, "bonus"));
      const wager = document.createElement("span");
      wager.className = "multiplier";
      wager.textContent = `${casino.wagering_multiplier}×`;
      const wagerCell = cell("Wagering", "");
      wagerCell.appendChild(wager);
      tr.appendChild(wagerCell);
      tr.appendChild(cell("Min. deposit", casino.minimum_deposit));
      const sourceCell = cell("Source", "");
      const url = new URL(casino.source_url);
      if (url.protocol !== "https:") throw new Error("Invalid source URL");
      const link = document.createElement("a");
      link.href = url.href;
      link.textContent = "View source ↗";
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.className = "source-link";
      sourceCell.appendChild(link);
      tr.appendChild(sourceCell);
      body.appendChild(tr);
    }
    status.hidden = true;
    tableWrap.hidden = false;
    count.textContent = `${data.casinos.length} casinos`;
    updated.textContent = data.updated_at ? new Date(data.updated_at).toLocaleString() : "Not available";
  } catch (error) {
    tableWrap.hidden = true;
    count.textContent = "Not ready";
    status.hidden = false;
    status.textContent = `Unable to display bonus data: ${error.message}`;
    console.error(error);
  }
}

loadBonuses();
