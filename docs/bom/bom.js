/* BOM checklist: data in window.BOM (data.js, generated from the part data). Ticks in localStorage. */
(function () {
  "use strict";
  const B = window.BOM;
  const KEY = "wd-bom-ticks-v1";
  const printMode = /[?&]print=1/.test(location.search);
  let ticks = {};
  try { ticks = printMode ? {} : JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { ticks = {}; }
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify(ticks)); } catch (e) { /* private mode */ } };
  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const fmt = (v, d) => (v == null || v === "" ? "" : Number(v).toFixed(d));

  // section: {id, title, note, groups: [{title, cols, rows}]} ; cols: [label, key, cls, fn]
  const sections = [];
  const matTitle = (m, t) => `${m.replace(/^\w/, (c) => c.toUpperCase())} ${t} mm`;

  // 1. laser parts grouped by material + thickness, rows in sheet order
  const lg = {};
  B.laser.forEach((r) => { const k = r.material + "|" + r.t; (lg[k] = lg[k] || []).push(r); });
  sections.push({
    id: "laser", title: "Laser-cut parts",
    note: `${B.meta.laser_parts} parts on ${B.meta.sheets} sheets. Balsa sheets 100 x 300 mm (grain along 300), ply and lite-ply 300 x 300 mm. The sheet file is in build-kit/laser/. Size = part bounding box in mm; area in cm2.`,
    groups: B.sheets.map((g) => ({
      title: `${matTitle(g.material, g.t)} — ${g.sheets} sheet(s), ${g.parts} parts`,
      cols: [["Part", "name", "n"], ["Assembly", "assembly"], ["Sheet file", "sheet", "f"], ["Size (mm)", "size", "num"], ["Area cm2", "area", "num"],
        ["Mass g", "mass", "num", (r) => fmt(r.mass, 1)], ["Arrow", "hint", "f"], ["Step", "step", "num"]],
      rows: lg[g.material + "|" + g.t] || [],
      prefix: "laser",
    })),
  });
  // 2. sheets to buy
  sections.push({
    id: "sheets", title: "Sheets to buy (balsa, ply, lite-ply)",
    note: "Computed from the nesting. Area = sheets x sheet size; part area = what the parts use. Buy 10-20 % extra balsa and choose it by weight.",
    groups: [{
      title: "", prefix: "sheet",
      cols: [["Material", "material"], ["Thickness mm", "t", "num"], ["Laser sheets", "sheets", "num"], ["Sheet (mm)", "sheet", "num", (r) => `${r.sheet[1]} x ${r.sheet[0]}`],
        ["Sheet area m2", "area_m2", "num", (r) => fmt(r.area_m2, 3)], ["Part area m2", "used_m2", "num", (r) => fmt(r.used_m2, 3)], ["Use %", "util", "num"],
        ["Buy", "buy"]],
      rows: B.sheets.map((g) => Object.assign({ id: g.material + "-" + g.t }, g)),
    }],
  });
  // 3. strip stock
  sections.push({
    id: "strips", title: "Strip and sheet stock (cut by hand)",
    note: "Not on the laser. Buy the stock lengths in the first table, then cut every part in the second table to length.",
    groups: [
      { title: "What to buy", prefix: "stock", cols: [["Stock", "stock"], ["Pieces", "pieces", "num"], ["Total mm", "total_mm", "num", (r) => fmt(r.total_mm, 0)], ["Buy", "buy"]],
        rows: B.stock.map((s) => Object.assign({ id: s.stock }, s)) },
      { title: "Every strip part", prefix: "strip", cols: [["Part", "name", "n"], ["Assembly", "assembly"], ["Material", "material"], ["Stock", "stock"], ["Section mm", "section", "num"],
        ["Length mm", "length", "num", (r) => fmt(r.length, 1)], ["Step", "step", "num"]], rows: B.strips },
    ],
  });
  // 4. prints
  const pg = {};
  B.prints.forEach((r) => { (pg[r.group] = pg[r.group] || []).push(r); });
  sections.push({
    id: "prints", title: "3D prints",
    note: "STL files in build-kit/print/. Jigs in PLA (3 walls, 20-30 % infill); aircraft parts in PETG. Everything fits a 256 mm bed.",
    groups: Object.keys(pg).map((g) => ({
      title: g, prefix: "print",
      cols: [["Part", "name", "n"], ["STL", "stl", "f"], ["Material", "material"], ["Qty", "qty", "num"], ["Size (mm)", "box", "num"], ["Note", "note"]],
      rows: pg[g],
    })),
  });
  // 5. electronics
  sections.push({
    id: "electronics", title: "Electronics",
    note: "From design/FIXED_MASSES.md and bom/BOM_Electronics_Robu.md (D-066). Weigh each part when it arrives.",
    groups: [{ title: "", prefix: "elec", cols: [["Item", "item"], ["Qty", "qty", "num"], ["Mass each", "mass", "num"], ["Where / note", "note"]],
      rows: B.electronics.map((r) => Object.assign({ id: r.item }, r)) }],
  });
  // 6. hardware, consumables
  sections.push({
    id: "hardware", title: "Hardware (quantities from the part data)",
    note: "Hinges, wire, rods, tubes, dowels, pins and screws: counted and measured from the model.",
    groups: [{ title: "", prefix: "hw", cols: [["Item", "item"], ["Qty", "qty", "num"], ["Note", "note"]], rows: B.hardware.map((r) => Object.assign({ id: r.item }, r)) }],
  });
  sections.push({
    id: "consumables", title: "Glue, film, bench and tools",
    note: "Film area from the mass-table film masses.",
    groups: [{ title: "", prefix: "cons", cols: [["Item", "item"], ["Qty", "qty", "num"], ["Note", "note"]], rows: B.consumables.map((r) => Object.assign({ id: r.item }, r)) }],
  });

  // ------------------------------------------------------------------ render
  const content = document.getElementById("content");
  const toc = document.getElementById("toc");
  const counters = [];
  sections.forEach((s) => {
    const sec = document.createElement("section");
    sec.id = s.id;
    let html = `<h2><span>${esc(s.title)}</span><span class="cnt" data-sec="${s.id}"></span></h2><p class="note">${esc(s.note)}</p>`;
    s.groups.forEach((g) => {
      if (g.title) html += `<h3>${esc(g.title)}</h3>`;
      html += "<table><thead><tr><th></th>" + g.cols.map((c) => `<th>${esc(c[0])}</th>`).join("") + "</tr></thead><tbody>";
      g.rows.forEach((r) => {
        const key = g.prefix + ":" + (r.id || r.name);
        html += `<tr data-key="${esc(key)}" data-sec="${s.id}" data-text="${esc(Object.values(r).join(" ").toLowerCase())}"><td class="c"><input type="checkbox" aria-label="have ${esc(r.name || r.item || r.stock || key)}"></td>` +
          g.cols.map((c) => `<td class="${c[2] || ""}">${esc(c[3] ? c[3](r) : r[c[1]])}</td>`).join("") + "</tr>";
      });
      html += "</tbody></table>";
    });
    sec.innerHTML = html;
    content.appendChild(sec);
    const a = document.createElement("a");
    a.href = "#" + s.id;
    a.innerHTML = `<span>${esc(s.title)}</span><span class="cnt" data-toc="${s.id}"></span>`;
    toc.appendChild(a);
  });
  const meta = document.createElement("p");
  meta.className = "note";
  meta.textContent = `Generated by ${B.meta.generated_by}. Online: ${B.meta.pages}bom/ · files: ${B.meta.repo}`;
  content.appendChild(meta);

  content.addEventListener("change", (e) => {
    const tr = e.target.closest("tr");
    if (!tr) return;
    if (e.target.checked) ticks[tr.dataset.key] = 1; else delete ticks[tr.dataset.key];
    save(); apply();
  });

  function apply() {
    const hide = document.getElementById("hide-done").checked;
    const q = document.getElementById("filter").value.trim().toLowerCase();
    const cnt = {};
    content.querySelectorAll("tr[data-key]").forEach((tr) => {
      const on = !!ticks[tr.dataset.key];
      tr.querySelector("input").checked = on;
      tr.classList.toggle("done", on);
      tr.classList.toggle("hidden", (hide && on) || (q && !tr.dataset.text.includes(q)));
      const c = (cnt[tr.dataset.sec] = cnt[tr.dataset.sec] || [0, 0]);
      c[1]++; if (on) c[0]++;
    });
    Object.entries(cnt).forEach(([s, [a, b]]) => {
      document.querySelectorAll(`[data-sec="${s}"].cnt, [data-toc="${s}"]`).forEach((el) => { el.textContent = `${a} / ${b}`; el.classList.toggle("full", a === b); });
    });
  }
  document.getElementById("hide-done").addEventListener("change", apply);
  document.getElementById("filter").addEventListener("input", apply);
  document.getElementById("btn-print").addEventListener("click", () => window.print());
  document.getElementById("btn-clear").addEventListener("click", () => { if (confirm("Clear every tick?")) { ticks = {}; save(); apply(); } });
  apply();
})();
