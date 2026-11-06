#!/usr/bin/env python3
"""Group Spotify Liked Songs into playlists by the year they were liked.

Usage:
  python3 spotify_liked_by_year.py CLIENT_ID            # dry run: just show counts per year
  python3 spotify_liked_by_year.py CLIENT_ID --apply    # create "Liked <year>" playlists

Uses the PKCE flow (no client secret). Redirect URI to register in your Spotify app:
  http://127.0.0.1:8888/callback
Standard library only.
"""
import base64, hashlib, http.server, json, secrets, sys, threading, time
import urllib.error, urllib.parse, urllib.request, webbrowser

REDIRECT = "http://127.0.0.1:8888/callback"
SCOPES = "user-library-read playlist-modify-private playlist-modify-public"
API = "https://api.spotify.com/v1"


def authorize(client_id):
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    state = secrets.token_urlsafe(16)
    result = {}

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path != "/callback":  # ignore favicon etc.
                self.send_response(404); self.end_headers(); return
            q = urllib.parse.parse_qs(parsed.query)
            result.update({k: v[0] for k, v in q.items()})
            self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.end_headers()
            self.wfile.write(b"Authorization complete. You can close this tab.")
        def log_message(self, *a): pass

    try:
        srv = http.server.HTTPServer(("127.0.0.1", 8888), H)
    except OSError:
        sys.exit("Port 8888 is already in use. Close the program using it and try again.")
    srv.timeout = 1
    deadline = time.time() + 300
    url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode({
        "client_id": client_id, "response_type": "code", "redirect_uri": REDIRECT,
        "scope": SCOPES, "state": state, "code_challenge_method": "S256", "code_challenge": challenge})
    print("Approve access in your browser:", url)
    webbrowser.open(url)
    while "state" not in result and "error" not in result and time.time() < deadline:
        srv.handle_request()
    srv.server_close()
    if "error" in result:
        sys.exit("Authorization was denied: %s" % result["error"])
    if result.get("state") != state or "code" not in result:
        sys.exit("Authorization failed or timed out.")
    body = urllib.parse.urlencode({
        "grant_type": "authorization_code", "code": result["code"], "redirect_uri": REDIRECT,
        "client_id": client_id, "code_verifier": verifier}).encode()
    req = urllib.request.Request("https://accounts.spotify.com/api/token", body)
    return json.load(urllib.request.urlopen(req))["access_token"]


def call(token, method, path, data=None):
    url = path if path.startswith("http") else API + path
    for _ in range(5):
        req = urllib.request.Request(url, json.dumps(data).encode() if data is not None else None, method=method)
        req.add_header("Authorization", "Bearer " + token)
        if data is not None: req.add_header("Content-Type", "application/json")
        try:
            raw = urllib.request.urlopen(req).read()
            return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(int(e.headers.get("Retry-After", "2")) + 1); continue
            raise
    raise RuntimeError("too many retries")


def main():
    if len(sys.argv) < 2: sys.exit(__doc__)
    client_id, apply = sys.argv[1], "--apply" in sys.argv
    token = authorize(client_id)

    by_year, url = {}, "/me/tracks?limit=50"
    while url:
        page = call(token, "GET", url)
        for it in page["items"]:
            tr = it["track"]
            if tr and tr.get("uri") and not tr.get("is_local"):
                by_year.setdefault(it["added_at"][:4], []).append(tr["uri"])
        url = page.get("next")

    total = sum(len(v) for v in by_year.values())
    print("\n%d liked songs in total:" % total)
    for y in sorted(by_year): print("  %s: %d songs" % (y, len(by_year[y])))
    if not apply:
        print("\nDry run only; nothing was changed. Add --apply to create the playlists."); return

    for y in sorted(by_year):
        pl = call(token, "POST", "/me/playlists", {
            "name": "Liked %s" % y, "public": False,
            "description": "Songs I liked in %s (auto-grouped)" % y})
        uris = by_year[y]
        for i in range(0, len(uris), 100):
            chunk = {"uris": uris[i:i + 100]}
            try:
                call(token, "POST", "/playlists/%s/tracks" % pl["id"], chunk)
            except urllib.error.HTTPError:
                call(token, "POST", "/playlists/%s/items" % pl["id"], chunk)
        print("Created Liked %s (%d songs)" % (y, len(uris)))
    print("Done. Your Liked Songs were not modified.")


main()
