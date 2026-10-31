/* md2docx: turn the Markdown a chatbot writes into a Word .docx file, in the browser, with no libraries.
   Handles headings, paragraphs, **bold**, *italic*, `code`, bullet and numbered lists, task boxes,
   block quotes and pipe tables. Works in browsers and in Node (for tests). */
(function (root) {
  const esc = s => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

  function runs(text, base = {}) {
    // Split on **bold**, *italic* / _italic_, `code`.
    const out = [];
    const re = /(\*\*[^*]+\*\*|__[^_]+__|`[^`]+`|\*[^*\s][^*]*\*|_[^_\s][^_]*_)/g;
    let last = 0, m;
    const push = (t, f) => { if (t) out.push(run(t, Object.assign({}, base, f))); };
    while ((m = re.exec(text))) {
      push(text.slice(last, m.index), {});
      const tok = m[0];
      if (tok.startsWith("**") || tok.startsWith("__")) push(tok.slice(2, -2), { b: true });
      else if (tok.startsWith("`")) push(tok.slice(1, -1), { code: true });
      else push(tok.slice(1, -1), { i: true });
      last = m.index + tok.length;
    }
    push(text.slice(last), {});
    return out.join("");
  }
  function run(t, f) {
    const pr = (f.b ? "<w:b/>" : "") + (f.i ? "<w:i/>" : "") +
      (f.code ? '<w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/>' : "");
    return `<w:r>${pr ? `<w:rPr>${pr}</w:rPr>` : ""}<w:t xml:space="preserve">${esc(t)}</w:t></w:r>`;
  }
  const para = (inner, style, extra = "") =>
    `<w:p>${style || extra ? `<w:pPr>${style ? `<w:pStyle w:val="${style}"/>` : ""}${extra}</w:pPr>` : ""}${inner}</w:p>`;
  const cleanInline = s => s.replace(/<br\s*\/?>/gi, " ").replace(/\[([^\]]+)\]\(([^)]+)\)/g, "$1 ($2)");

  function table(rows) {
    const cells = r => r.replace(/^\s*\|/, "").replace(/\|\s*$/, "").split("|").map(c => c.trim());
    const head = cells(rows[0]);
    const body = rows.slice(2).map(cells);
    const n = head.length;
    const tc = (t, hdr) => `<w:tc><w:tcPr><w:tcW w:w="0" w:type="auto"/>${hdr ? '<w:shd w:val="clear" w:color="auto" w:fill="E3EEF6"/>' : ""}</w:tcPr>${para(runs(cleanInline(t), hdr ? { b: true } : {}), "TableText")}</w:tc>`;
    const tr = (r, hdr) => `<w:tr>${hdr ? "<w:trPr><w:tblHeader/></w:trPr>" : ""}${Array.from({ length: n }, (_, i) => tc(r[i] || "", hdr)).join("")}</w:tr>`;
    return `<w:tbl><w:tblPr><w:tblStyle w:val="TableGrid"/><w:tblW w:w="5000" w:type="pct"/></w:tblPr>` +
      `<w:tblGrid>${"<w:gridCol/>".repeat(n)}</w:tblGrid>${tr(head, true)}${body.map(r => tr(r, false)).join("")}</w:tbl>` + para("", "");
  }

  function bodyXml(md) {
    const lines = md.replace(/\r\n?/g, "\n").split("\n");
    const out = [];
    let i = 0, inCode = false;
    while (i < lines.length) {
      let l = lines[i];
      if (/^\s*```/.test(l)) { inCode = !inCode; i++; continue; }
      if (inCode) { out.push(para(run(l, { code: true }), "")); i++; continue; }
      if (/^\s*\|.*\|\s*$/.test(l) && i + 1 < lines.length && /^\s*\|?\s*:?-{2,}/.test(lines[i + 1])) {
        const rows = [];
        while (i < lines.length && /^\s*\|.*\|\s*$/.test(lines[i])) rows.push(lines[i++]);
        out.push(table(rows)); continue;
      }
      if (!l.trim()) { i++; continue; }
      if (/^\s*(-{3,}|\*{3,}|_{3,})\s*$/.test(l)) { i++; continue; }
      let m;
      if ((m = l.match(/^(#{1,4})\s+(.*)$/))) { out.push(para(runs(cleanInline(m[2])), "Heading" + m[1].length)); i++; continue; }
      if ((m = l.match(/^\s*[-*+]\s+\[( |x|X)\]\s+(.*)$/))) { out.push(para(run(m[1].trim() ? "☑ " : "☐ ", {}) + runs(cleanInline(m[2])), "ListBullet")); i++; continue; }
      if ((m = l.match(/^(\s*)[-*+]\s+(.*)$/))) { out.push(para(runs(cleanInline(m[2])), m[1].length >= 2 ? "ListBullet2" : "ListBullet")); i++; continue; }
      if ((m = l.match(/^\s*(\d+)[.)]\s+(.*)$/))) { out.push(para(run(m[1] + ". ", {}) + runs(cleanInline(m[2])), "ListNumberPlain")); i++; continue; }
      if ((m = l.match(/^\s*>\s?(.*)$/))) { out.push(para(runs(cleanInline(m[1])), "Quote")); i++; continue; }
      // paragraph: join following plain lines
      const buf = [l.trim()];
      while (i + 1 < lines.length && lines[i + 1].trim() && !/^(\s*[-*+>|#]|\s*\d+[.)]\s|\s*```)/.test(lines[i + 1])) buf.push(lines[++i].trim());
      out.push(para(runs(cleanInline(buf.join(" "))), ""));
      i++;
    }
    return out.join("");
  }

  const W = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"';
  function files(md, title) {
    const doc = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document ${W}><w:body>${bodyXml(md)}` +
      `<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1080" w:right="1080" w:bottom="1080" w:left="1080" w:header="720" w:footer="720" w:gutter="0"/></w:sectPr></w:body></w:document>`;
    const st = (id, name, ppr, rpr, type = "paragraph") => `<w:style w:type="${type}" w:styleId="${id}"><w:name w:val="${name}"/><w:basedOn w:val="Normal"/><w:qFormat/>${ppr ? `<w:pPr>${ppr}</w:pPr>` : ""}${rpr ? `<w:rPr>${rpr}</w:rPr>` : ""}</w:style>`;
    const styles = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:styles ${W}>` +
      `<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:cs="Calibri"/><w:sz w:val="22"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="264" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>` +
      `<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/></w:style>` +
      st("Heading1", "heading 1", '<w:keepNext/><w:spacing w:before="240" w:after="120"/><w:outlineLvl w:val="0"/>', '<w:b/><w:color w:val="1F5F8B"/><w:sz w:val="36"/>') +
      st("Heading2", "heading 2", '<w:keepNext/><w:spacing w:before="240" w:after="80"/><w:outlineLvl w:val="1"/>', '<w:b/><w:color w:val="1F5F8B"/><w:sz w:val="28"/>') +
      st("Heading3", "heading 3", '<w:keepNext/><w:spacing w:before="160" w:after="60"/><w:outlineLvl w:val="2"/>', '<w:b/><w:sz w:val="24"/>') +
      st("Heading4", "heading 4", '<w:keepNext/><w:outlineLvl w:val="3"/>', '<w:b/><w:i/>') +
      st("ListBullet", "List Bullet", '<w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr><w:spacing w:after="40"/>', "") +
      st("ListBullet2", "List Bullet 2", '<w:numPr><w:ilvl w:val="1"/><w:numId w:val="1"/></w:numPr><w:spacing w:after="40"/>', "") +
      st("ListNumberPlain", "List Number Plain", '<w:ind w:left="360" w:hanging="360"/><w:spacing w:after="40"/>', "") +
      st("Quote", "Quote", '<w:ind w:left="360"/><w:pBdr><w:left w:val="single" w:sz="12" w:space="8" w:color="1F5F8B"/></w:pBdr>', '<w:color w:val="404040"/>') +
      st("TableText", "Table Text", '<w:spacing w:before="20" w:after="20"/>', '<w:sz w:val="18"/>') +
      `<w:style w:type="table" w:styleId="TableGrid"><w:name w:val="Table Grid"/><w:tblPr><w:tblBorders><w:top w:val="single" w:sz="4" w:color="BFC8CF"/><w:left w:val="single" w:sz="4" w:color="BFC8CF"/><w:bottom w:val="single" w:sz="4" w:color="BFC8CF"/><w:right w:val="single" w:sz="4" w:color="BFC8CF"/><w:insideH w:val="single" w:sz="4" w:color="BFC8CF"/><w:insideV w:val="single" w:sz="4" w:color="BFC8CF"/></w:tblBorders><w:tblCellMar><w:left w:w="80" w:type="dxa"/><w:right w:w="80" w:type="dxa"/></w:tblCellMar></w:tblPr></w:style></w:styles>`;
    const numbering = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:numbering ${W}><w:abstractNum w:abstractNumId="0">` +
      `<w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="•"/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="360" w:hanging="260"/></w:pPr></w:lvl>` +
      `<w:lvl w:ilvl="1"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="–"/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="720" w:hanging="260"/></w:pPr></w:lvl>` +
      `</w:abstractNum><w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num></w:numbering>`;
    const core = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>${esc(title || "Helper roles")}</dc:title><dc:creator>ERI Helper Kit</dc:creator></cp:coreProperties>`;
    return {
      "[Content_Types].xml": `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/><Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/><Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/></Types>`,
      "_rels/.rels": `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/></Relationships>`,
      "word/_rels/document.xml.rels": `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/></Relationships>`,
      "word/document.xml": doc, "word/styles.xml": styles, "word/numbering.xml": numbering, "docProps/core.xml": core
    };
  }

  // Minimal ZIP writer (stored, no compression) with CRC-32.
  const CRC = (() => { const t = new Uint32Array(256); for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1; t[n] = c >>> 0; } return t; })();
  const crc32 = b => { let c = 0xFFFFFFFF; for (let i = 0; i < b.length; i++) c = CRC[(c ^ b[i]) & 255] ^ (c >>> 8); return (c ^ 0xFFFFFFFF) >>> 0; };
  function zip(fileMap) {
    const enc = new TextEncoder(), parts = [], central = []; let off = 0;
    const u16 = v => [v & 255, (v >>> 8) & 255], u32 = v => [v & 255, (v >>> 8) & 255, (v >>> 16) & 255, (v >>> 24) & 255];
    for (const [name, text] of Object.entries(fileMap)) {
      const nb = enc.encode(name), data = enc.encode(text), c = crc32(data);
      const local = [...u32(0x04034b50), ...u16(20), ...u16(0x0800), ...u16(0), ...u16(0), ...u16(0x21), ...u32(c), ...u32(data.length), ...u32(data.length), ...u16(nb.length), ...u16(0)];
      parts.push(Uint8Array.from(local), nb, data);
      central.push(Uint8Array.from([...u32(0x02014b50), ...u16(20), ...u16(20), ...u16(0x0800), ...u16(0), ...u16(0), ...u16(0x21), ...u32(c), ...u32(data.length), ...u32(data.length), ...u16(nb.length), ...u16(0), ...u16(0), ...u16(0), ...u16(0), ...u32(0), ...u32(off)]), nb);
      off += local.length + nb.length + data.length;
    }
    const cdSize = central.reduce((s, a) => s + a.length, 0), count = Object.keys(fileMap).length;
    const end = Uint8Array.from([...u32(0x06054b50), ...u16(0), ...u16(0), ...u16(count), ...u16(count), ...u32(cdSize), ...u32(off), ...u16(0)]);
    const all = [...parts, ...central, end], total = all.reduce((s, a) => s + a.length, 0), out = new Uint8Array(total);
    let p = 0; for (const a of all) { out.set(a, p); p += a.length; } return out;
  }
  const md2docx = (md, title) => zip(files(md, title));
  if (typeof module !== "undefined") module.exports = { md2docx };
  else root.md2docx = md2docx;
})(this);
