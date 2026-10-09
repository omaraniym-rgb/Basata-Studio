// Basata Journal markdown: small, predictable, made for one writer.
//   ## Heading        ### Small heading
//   > Pull quote      - List item      1. Numbered item      ---  divider
//   ![Alt text](image-url)            figure (add "cutout" as title for images with no background)
//   **bold**  *italic*  [link](https://…)
//   A block that starts with "<" is kept as raw HTML (for special figures).

export const esc = s => String(s == null ? '' : s)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

function inline(t) {
  t = esc(t);
  t = t.replace(/`([^`]+)`/g, '<code>$1</code>');
  t = t.replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>');
  t = t.replace(/(^|[^*\w])\*([^*\n]+)\*(?!\w)/g, '$1<em>$2</em>');
  t = t.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (m, txt, url) => {
    const ext = /^https?:\/\//.test(url) && !/^https?:\/\/(www\.)?basata\.studio/.test(url);
    return `<a href="${url}"${ext ? ' target="_blank" rel="noopener"' : ''}>${txt}</a>`;
  });
  return t;
}

function figure(alt, src, title) {
  const cut = /cutout/i.test(title || '');
  return `<figure class="fig${cut ? ' cut' : ''}"><img src="${esc(src)}" alt="${esc(alt)}" loading="lazy" decoding="async"></figure>`;
}

export function md(src) {
  const blocks = String(src || '').replace(/\r/g, '').split(/\n\s*\n/);
  const out = [];
  for (let b of blocks) {
    b = b.replace(/^\n+|\s+$/g, '');
    if (!b) continue;
    if (/^\s*</.test(b)) { out.push(b); continue; }                              // raw HTML
    let m;
    if ((m = b.match(/^!\[([^\]]*)\]\(([^)\s]+)(?:\s+"([^"]*)")?\)$/))) { out.push(figure(m[1], m[2], m[3])); continue; }
    if (/^---+$/.test(b)) { out.push('<hr>'); continue; }
    if ((m = b.match(/^(#{2,3})\s+(.+)$/))) { const n = m[1].length; out.push(`<h${n}>${inline(m[2])}</h${n}>`); continue; }
    const lines = b.split('\n');
    if (lines.every(l => /^>\s?/.test(l))) { out.push(`<p class="pull">${inline(lines.map(l => l.replace(/^>\s?/, '')).join(' '))}</p>`); continue; }
    if (lines.every(l => /^[-*]\s+/.test(l))) { out.push('<ul>' + lines.map(l => `<li>${inline(l.replace(/^[-*]\s+/, ''))}</li>`).join('') + '</ul>'); continue; }
    if (lines.every(l => /^\d+[.)]\s+/.test(l))) { out.push('<ol>' + lines.map(l => `<li>${inline(l.replace(/^\d+[.)]\s+/, ''))}</li>`).join('') + '</ol>'); continue; }
    // a paragraph may still contain an image line on its own: split those out
    let para = [];
    const flush = () => { if (para.length) { out.push(`<p>${inline(para.join(' '))}</p>`); para = []; } };
    for (const l of lines) {
      const im = l.match(/^!\[([^\]]*)\]\(([^)\s]+)(?:\s+"([^"]*)")?\)$/);
      if (im) { flush(); out.push(figure(im[1], im[2], im[3])); } else para.push(l.trim());
    }
    flush();
  }
  return out.join('\n');
}

export function words(src) {
  return String(src || '').replace(/<[^>]+>/g, ' ').replace(/[#>*_`!\[\]()-]/g, ' ').split(/\s+/).filter(Boolean).length;
}

// Typography rule: no line ever ends with a single word or a one-letter word.
function tie(t) {
  t = t.replace(/(^|[^\w&])([AaI])\s+(?=\w)/g, (m, p, w) => p + w + ' ');
  return t.replace(/(\S+)\s+(\S+)(\s*)$/, (m, a, b, c) => a + ' ' + b + c);
}
export function nowidows(html) {
  let skip = 0;
  return html.replace(/<[^>]+>|[^<]+/g, t => {
    if (t[0] === '<') {
      const m = t.match(/^<\/?([a-zA-Z0-9]+)/); const n = m ? m[1].toLowerCase() : '';
      if (['script', 'style', 'svg', 'pre', 'code', 'title', 'textarea'].includes(n)) skip = Math.max(0, skip + (t[1] === '/' ? -1 : 1));
      return t;
    }
    return skip || !t.trim() ? t : tie(t);
  });
}
