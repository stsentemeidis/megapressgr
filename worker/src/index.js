/**
 * Megapress Admin Worker
 *
 * Serves the admin UI (static assets) and a small API that:
 *  - uploads original photos to R2 (_incoming/) and triggers the GitHub Action
 *    that watermarks + thumbnails them and publishes the event
 *  - edits the site's data files (upcoming / partners / clients / stats) via the
 *    GitHub API, which the rebuild Action turns back into the live site
 *  - deletes events/items (and cleans their photos from R2)
 *  - suggests tags for an event name via Workers AI
 *
 * Access to this Worker is restricted by Cloudflare Access (email allow-list).
 *
 * Bindings / vars (see wrangler.toml):
 *   MEDIA         R2 bucket (megapress-media)
 *   ASSETS        static assets (the admin UI in ./public)
 *   AI            Workers AI (optional, for suggest-tags)
 *   GITHUB_REPO   "owner/repo"          (var)
 *   GITHUB_BRANCH "main"                (var)
 *   MEDIA_BASE    "https://media.megapressevents.com" (var)
 *   GITHUB_TOKEN  fine-grained PAT with Contents: read/write  (secret)
 */

const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj), { status, headers: { "content-type": "application/json" } });

// ---------- GitHub helpers ----------
function gh(env, path, init = {}) {
  return fetch(`https://api.github.com/repos/${env.GITHUB_REPO}${path}`, {
    ...init,
    headers: {
      "Authorization": `Bearer ${env.GITHUB_TOKEN}`,
      "Accept": "application/vnd.github+json",
      "User-Agent": "megapress-admin-worker",
      ...(init.headers || {}),
    },
  });
}
async function ghGetFile(env, filePath) {
  const r = await gh(env, `/contents/${encodeURI(filePath)}?ref=${env.GITHUB_BRANCH}`);
  if (!r.ok) throw new Error(`GitHub read ${filePath}: ${r.status}`);
  const j = await r.json();
  const content = decodeURIComponent(escape(atob(j.content.replace(/\n/g, ""))));
  return { data: JSON.parse(content), sha: j.sha };
}
async function ghPutFile(env, filePath, dataObj, sha, message) {
  const body = btoa(unescape(encodeURIComponent(JSON.stringify(dataObj, null, 2) + "\n")));
  const r = await gh(env, `/contents/${encodeURI(filePath)}`, {
    method: "PUT",
    body: JSON.stringify({ message, content: body, sha, branch: env.GITHUB_BRANCH }),
  });
  if (!r.ok) throw new Error(`GitHub write ${filePath}: ${r.status} ${await r.text()}`);
  return r.json();
}
async function ghDispatch(env, event_type, client_payload) {
  const r = await gh(env, `/dispatches`, {
    method: "POST",
    body: JSON.stringify({ event_type, client_payload }),
  });
  if (!r.ok) throw new Error(`GitHub dispatch: ${r.status} ${await r.text()}`);
}

const slug = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");

// ---------- API ----------
async function handleApi(request, env, url) {
  const p = url.pathname.replace(/^\/api\//, "");

  // GET /api/data — current content for the Manage/edit views
  if (p === "data" && request.method === "GET") {
    const names = ["events", "upcoming", "partners", "clients", "stats"];
    const out = {};
    for (const n of names) out[n] = (await ghGetFile(env, `data/${n}.json`)).data;
    return json(out);
  }

  // POST /api/upload?folder=..&name=..  (raw body = original photo bytes)
  if (p === "upload" && request.method === "POST") {
    const folder = url.searchParams.get("folder");
    const name = url.searchParams.get("name");
    if (!folder || !name) return json({ error: "missing folder/name" }, 400);
    await env.MEDIA.put(`_incoming/${folder}/${name}`, await request.arrayBuffer(), {
      httpMetadata: { contentType: "image/jpeg" },
    });
    return json({ ok: true });
  }

  // POST /api/upload-logo?id=..  (raw body = processed monochrome PNG)
  if (p === "upload-logo" && request.method === "POST") {
    const id = url.searchParams.get("id");
    if (!id) return json({ error: "missing id" }, 400);
    const key = `logos/${id}.png`;
    await env.MEDIA.put(key, await request.arrayBuffer(), { httpMetadata: { contentType: "image/png" } });
    return json({ ok: true, url: `${env.MEDIA_BASE}/${key}` });
  }

  // POST /api/add-event — triggers the processing Action
  if (p === "add-event" && request.method === "POST") {
    const ev = await request.json();
    ev.id = ev.id || `${slug(ev.name)}-${ev.year}`;
    ev.folder = ev.folder || `${ev.category === "exhibition" ? "Exhibitions" : "Events"}/${ev.name}`;
    await ghDispatch(env, "process-event", ev);
    return json({ ok: true, id: ev.id });
  }

  // POST /api/add-upcoming
  if (p === "add-upcoming" && request.method === "POST") {
    const u = await request.json();
    u.id = u.id || `${slug(u.name)}-${u.year}`;
    const { data, sha } = await ghGetFile(env, "data/upcoming.json");
    const next = data.filter((x) => x.id !== u.id);
    next.push(u);
    await ghPutFile(env, "data/upcoming.json", next, sha, `Add upcoming: ${u.name}`);
    return json({ ok: true });
  }

  // POST /api/save-partner  and  /api/save-client
  if ((p === "save-partner" || p === "save-client") && request.method === "POST") {
    const item = await request.json();
    item.id = item.id || slug(item.name);
    const file = p === "save-partner" ? "data/partners.json" : "data/clients.json";
    const { data, sha } = await ghGetFile(env, file);
    const next = data.filter((x) => x.id !== item.id);
    next.push(item);
    await ghPutFile(env, file, next, sha, `Update ${p === "save-partner" ? "partner" : "client"}: ${item.name}`);
    return json({ ok: true });
  }

  // POST /api/save-stats  (full array)
  if (p === "save-stats" && request.method === "POST") {
    const stats = await request.json();
    const { sha } = await ghGetFile(env, "data/stats.json");
    await ghPutFile(env, "data/stats.json", stats, sha, "Update stats");
    return json({ ok: true });
  }

  // POST /api/delete  { type, id }
  if (p === "delete" && request.method === "POST") {
    const { type, id } = await request.json();
    const fileMap = { event: "data/events.json", upcoming: "data/upcoming.json", partner: "data/partners.json", client: "data/clients.json" };
    const file = fileMap[type];
    if (!file) return json({ error: "bad type" }, 400);
    const { data, sha } = await ghGetFile(env, file);
    const target = data.find((x) => x.id === id);
    const next = data.filter((x) => x.id !== id);
    await ghPutFile(env, file, next, sha, `Delete ${type}: ${id}`);
    // clean R2 photos for a deleted event
    if (type === "event" && target && target.folder) {
      for (const prefix of [`thumbs/${target.folder}/`, `watermarked/${target.folder}/`]) {
        const listed = await env.MEDIA.list({ prefix });
        for (const o of listed.objects) await env.MEDIA.delete(o.key);
      }
    }
    return json({ ok: true });
  }

  // POST /api/suggest-tags  { name }
  if (p === "suggest-tags" && request.method === "POST") {
    const { name } = await request.json();
    if (!env.AI) return json({ tags: [] });
    const prompt = `You label photography portfolio events. For the event titled "${name}", suggest 1 or 2 very short tags (max 3 words each) a viewer would find useful, such as a headline figure, an honoured country, or the organiser. Reply ONLY as a JSON array of strings. If unsure, reply [].`;
    try {
      const res = await env.AI.run("@cf/meta/llama-3.1-8b-instruct", { messages: [{ role: "user", content: prompt }] });
      const text = (res.response || "").trim();
      const m = text.match(/\[[\s\S]*\]/);
      const tags = m ? JSON.parse(m[0]) : [];
      return json({ tags: Array.isArray(tags) ? tags.slice(0, 2) : [] });
    } catch (e) {
      return json({ tags: [] });
    }
  }

  return json({ error: "not found" }, 404);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    try {
      if (url.pathname.startsWith("/api/")) return await handleApi(request, env, url);
    } catch (e) {
      return json({ error: String(e && e.message || e) }, 500);
    }
    // everything else → the admin UI (static assets)
    return env.ASSETS.fetch(request);
  },
};
