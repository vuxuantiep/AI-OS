import dashboardHtml from "./04_Infrastruktur/Gateway/templates/dashboard.html";

// Basic Auth: Benutzer "ceo", Passwort im Secret DASHBOARD_PASSWORD
// (setzen mit: npx wrangler secret put DASHBOARD_PASSWORD)
async function isAuthorized(request, env) {
  const header = request.headers.get("Authorization") || "";
  if (!header.startsWith("Basic ")) return false;
  let decoded;
  try {
    decoded = atob(header.slice(6));
  } catch {
    return false;
  }
  const enc = new TextEncoder();
  const [given, expected] = await Promise.all([
    crypto.subtle.digest("SHA-256", enc.encode(decoded)),
    crypto.subtle.digest("SHA-256", enc.encode(`ceo:${env.DASHBOARD_PASSWORD}`)),
  ]);
  return crypto.subtle.timingSafeEqual(given, expected);
}

export default {
  async fetch(request, env) {
    if (!env.DASHBOARD_PASSWORD) {
      return new Response("Konfigurationsfehler: Secret DASHBOARD_PASSWORD fehlt.", { status: 500 });
    }
    if (!(await isAuthorized(request, env))) {
      return new Response("Authentifizierung erforderlich", {
        status: 401,
        headers: { "WWW-Authenticate": 'Basic realm="AI-OS CEO Dashboard"' },
      });
    }

    // Durch den Cloudflare Tunnel zum lokalen AI-OS (DNS des Hostnamens zeigt auf den Tunnel)
    try {
      const resp = await fetch(request);
      if ([502, 503, 530].includes(resp.status)) {
        throw new Error(`Origin-Fehler ${resp.status}`);
      }
      return resp;
    } catch {
      // PC aus oder Tunnel offline: Seite als statischer Fallback, APIs mit klarer Meldung
      const url = new URL(request.url);
      if (url.pathname === "/" || url.pathname === "/index.html") {
        return new Response(dashboardHtml, {
          headers: { "Content-Type": "text/html; charset=utf-8" },
        });
      }
      return Response.json(
        { error: "Lokales AI-OS nicht erreichbar — PC ausgeschaltet oder Tunnel offline." },
        { status: 503 },
      );
    }
  },
};
