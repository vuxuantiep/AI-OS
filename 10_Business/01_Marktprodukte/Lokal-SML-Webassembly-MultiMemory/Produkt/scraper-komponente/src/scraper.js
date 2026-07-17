// feed-scraper — läuft als Wasm-Komponente (componentize-js/StarlingMonkey).
// Kein DOMParser in dieser Laufzeit → bewusst Regex-Parsing für RSS 2.0 + Atom.

const MAX_ITEMS = 50;
const MAX_TEXT = 1500;

function entschaerfen(s) {
  return s
    .replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, "$1")
    .replace(/<[^>]+>/g, " ")
    .replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&")
    .replace(/&quot;/g, '"').replace(/&#39;|&apos;/g, "'")
    .replace(/\s+/g, " ")
    .trim();
}

function feld(block, ...tags) {
  for (const t of tags) {
    const m = block.match(new RegExp(`<${t}[^>]*>([\\s\\S]*?)</${t}>`, "i"));
    if (m) return entschaerfen(m[1]);
  }
  return "";
}

function atomLink(block) {
  // Atom: <link href="..."/> — bevorzugt rel="alternate" oder ohne rel
  const links = [...block.matchAll(/<link\b([^>]*)\/?>(?:<\/link>)?/gi)];
  for (const l of links) {
    const attrs = l[1];
    const rel = (attrs.match(/rel="([^"]*)"/i) || [])[1];
    const href = (attrs.match(/href="([^"]*)"/i) || [])[1];
    if (href && (!rel || rel === "alternate")) return href;
  }
  return "";
}

function parseFeed(xml) {
  const items = [];
  // RSS 2.0: <item>, Atom: <entry>
  const bloecke = [...xml.matchAll(/<(item|entry)\b[\s\S]*?<\/\1>/gi)].map(m => m[0]);
  for (const block of bloecke.slice(0, MAX_ITEMS)) {
    const titel = feld(block, "title");
    let link = feld(block, "link");
    if (!link || !/^https?:/i.test(link)) link = atomLink(block) || link;
    const datum = feld(block, "pubDate", "published", "updated", "dc:date").slice(0, 40);
    const text = (feld(block, "content:encoded", "content", "description", "summary")).slice(0, MAX_TEXT);
    if (titel || link) items.push({ titel, link, datum, text });
  }
  return items;
}

export const scraper = {
  async fetchFeed(url) {
    if (!/^https:\/\//i.test(url)) {
      throw "Nur https:// Feed-URLs erlaubt: " + url;
    }
    let resp;
    try {
      resp = await fetch(url, { headers: { "user-agent": "themen-assistent/0.1 (+feed-reader)" } });
    } catch (e) {
      throw "Netzwerk verweigert oder nicht erreichbar (" + url + "): " + String(e);
    }
    if (!resp.ok) throw "HTTP " + resp.status + " für " + url;
    const xml = await resp.text();
    const items = parseFeed(xml);
    if (items.length === 0) throw "Kein RSS/Atom-Inhalt erkannt: " + url;
    return items;
  },
};
