---
name: spotify-liked-by-year
description: Group a user's Spotify Liked Songs into playlists by the year they saved (liked) each track, not by release year. Use when the user wants to organize, split, or archive Liked Songs by year, e.g. "group my liked songs by year" or "make a playlist for each year I liked songs".
---

# Spotify Liked Songs by Year Saved

Creates one private playlist per year ("Liked 2021", "Liked 2022", ...) from the user's Liked Songs, using the date each song was liked (`added_at`). Liked Songs itself is never modified.

The work is done by `scripts/spotify_liked_by_year.py` in this skill's folder. It uses only the Python 3 standard library and the Spotify PKCE login flow (no client secret).

## Running the script

- **Paths:** the script path is relative to this skill's folder. Either `cd` into the skill folder first, or use the full path, e.g. `python3 ~/.claude/skills/spotify-liked-by-year/scripts/spotify_liked_by_year.py` (adjust if the skill is installed elsewhere).
- **Timeout:** the script waits up to 300 seconds for the user to approve access in the browser. A Bash call's default timeout is 120 seconds, so run it with a long timeout (e.g. 600000 ms) or in the background, and tell the user to approve in the browser promptly.
- `--help` prints usage. The Client ID must be the 32-character hex string from the Spotify app's Settings page; the script rejects anything else.

## Steps

1. **Check the user has a Spotify Client ID.** If not, walk them through creating one:
   - Go to https://developer.spotify.com/dashboard, log in, and click **Create app**.
   - Redirect URI: `http://127.0.0.1:8888/callback` (click **Add**).
   - API: tick **Web API**. The user must accept Spotify's developer terms themselves.
   - Open the app's **Settings** and copy the **Client ID**. Never ask for the Client Secret or any password.
   - Note: Spotify development-mode apps may require a Premium account.

2. **Dry run first** (changes nothing):
   ```bash
   python3 scripts/spotify_liked_by_year.py CLIENT_ID
   ```
   A browser tab opens for the user to approve access. Report the per-year counts back.

3. **Ask the user to confirm** before creating anything. Offer to change the playlist naming if they want.

4. **Create the playlists:**
   ```bash
   python3 scripts/spotify_liked_by_year.py CLIENT_ID --apply
   ```
   Approval is requested again in the browser, and all Liked Songs are re-read. If the user liked new songs since the dry run, the counts will be higher than previewed; that is expected.

## If something goes wrong

- **HTTP 403:** the Spotify app is in development mode and the user's account is not allowed to use it. Tell them to open their app on the Developer Dashboard, go to **User Management** (under Settings), and add their own Spotify account email, then retry.
- **Port 8888 in use:** close whatever is using it and retry.
- **Authorization denied or timed out:** nothing was changed; just run the command again.
- **Error partway through `--apply`:** the script lists the playlists it already created, marking finished ones "(complete)". Ask the user to delete any incomplete "Liked YYYY" playlist (and any they want to redo) in Spotify before re-running, otherwise duplicates are created.

## Things to tell the user

- Grouping is by the year they **liked** the song, not the song's release year.
- Playlists are created as **private**; the user can make them public in Spotify.
- Local files cannot be added to playlists by the Spotify API and are skipped.
- Running `--apply` again creates duplicate playlists; it does not merge into existing ones.
- Never hard-code or commit a Client ID or access token.
