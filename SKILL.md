---
name: spotify-liked-by-year
description: Group a user's Spotify Liked Songs into playlists by the year they saved (liked) each track, not by release year. Use when the user wants to organize, split, or archive Liked Songs by year, e.g. "group my liked songs by year" or "make a playlist for each year I liked songs".
---

# Spotify Liked Songs by Year Saved

Creates one private playlist per year ("Liked 2021", "Liked 2022", ...) from the user's Liked Songs, using the date each song was liked (`added_at`). Liked Songs itself is never modified.

The work is done by `scripts/spotify_liked_by_year.py` in this skill's folder. It uses only the Python 3 standard library and the Spotify PKCE login flow (no client secret).

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
   Approval is requested again in the browser.

## Things to tell the user

- Grouping is by the year they **liked** the song, not the song's release year.
- Playlists are created as **private**; the user can make them public in Spotify.
- Local files cannot be added to playlists by the Spotify API and are skipped.
- Running `--apply` again creates duplicate playlists; it does not merge into existing ones.
- Never hard-code or commit a Client ID or access token.
