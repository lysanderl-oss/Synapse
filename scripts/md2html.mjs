// Convert markdown to styled HTML for PDF generation
// Usage: node md2html.mjs <input.md> <output.html>
import fs from 'fs';
import path from 'path';
import { marked } from 'marked';

const [, , inputPath, outputPath] = process.argv;
if (!inputPath || !outputPath) {
  console.error('Usage: node md2html.mjs <input.md> <output.html>');
  process.exit(1);
}

const md = fs.readFileSync(inputPath, 'utf-8');
const bodyHtml = marked.parse(md);
const title = path.basename(inputPath, '.md');

const html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>${title}</title>
<style>
@page { size: A4; margin: 18mm 16mm; }
body {
  font-family: "Microsoft YaHei", "PingFang SC", "Hiragino Sans GB", "Noto Sans CJK SC", "Arial Unicode MS", "Segoe UI", sans-serif;
  font-size: 10.5pt;
  line-height: 1.55;
  color: #1f2937;
  max-width: 100%;
  margin: 0;
  padding: 0;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}
h1 {
  font-size: 22pt;
  font-weight: 700;
  margin: 0 0 0.4em 0;
  padding-bottom: 0.3em;
  border-bottom: 3px solid #2563eb;
  color: #0f172a;
  page-break-after: avoid;
}
h2 {
  font-size: 15pt;
  font-weight: 700;
  margin: 1.4em 0 0.5em 0;
  padding-bottom: 0.25em;
  border-bottom: 1.5px solid #cbd5e1;
  color: #1e3a8a;
  page-break-after: avoid;
}
h3 {
  font-size: 12pt;
  font-weight: 700;
  margin: 1.1em 0 0.4em 0;
  color: #1e40af;
  page-break-after: avoid;
}
h4 {
  font-size: 11pt;
  font-weight: 600;
  margin: 0.8em 0 0.3em 0;
  color: #374151;
}
p { margin: 0.5em 0; }
ul, ol { margin: 0.4em 0; padding-left: 1.6em; }
li { margin: 0.2em 0; }
strong { color: #0f172a; font-weight: 700; }
em { color: #475569; }
blockquote {
  margin: 0.7em 0;
  padding: 0.5em 1em;
  border-left: 4px solid #3b82f6;
  background: #eff6ff;
  color: #334155;
  font-style: normal;
}
hr { border: none; border-top: 1px dashed #94a3b8; margin: 1.4em 0; }
code {
  font-family: "Consolas", "Monaco", monospace;
  font-size: 9.5pt;
  background: #f1f5f9;
  padding: 1px 5px;
  border-radius: 3px;
  color: #be123c;
}
pre {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  padding: 0.7em 1em;
  overflow-x: auto;
  font-size: 9.5pt;
  line-height: 1.4;
  page-break-inside: avoid;
}
pre code {
  background: transparent;
  padding: 0;
  color: #0f172a;
}
table {
  border-collapse: collapse;
  width: 100%;
  margin: 0.7em 0;
  font-size: 9.5pt;
  page-break-inside: avoid;
}
th, td {
  border: 1px solid #cbd5e1;
  padding: 5px 8px;
  text-align: left;
  vertical-align: top;
}
th { background: #e0e7ff; font-weight: 700; color: #1e3a8a; }
tr:nth-child(even) td { background: #f8fafc; }
a { color: #2563eb; text-decoration: none; }
.footer {
  margin-top: 2em;
  padding-top: 0.8em;
  border-top: 1px solid #cbd5e1;
  font-size: 9pt;
  color: #64748b;
  text-align: center;
}
</style>
</head>
<body>
${bodyHtml}
<div class="footer">Synapse-PJ · Lysander AI CEO · ${new Date().toISOString().split('T')[0]}</div>
</body>
</html>`;

fs.writeFileSync(outputPath, html, 'utf-8');
console.log('HTML generated:', outputPath, '(' + html.length + ' bytes)');
