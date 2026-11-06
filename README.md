# Spotify Liked Songs by Year

Spotify can't group your Liked Songs. This tool creates one private playlist per year (`Liked 2021`, `Liked 2022`, ...) based on **the year you liked each song**, not the song's release year.

- Your Liked Songs are never changed or deleted. Songs are only copied into new playlists.
- Dry run by default: it shows how many songs fall in each year and changes nothing until you add `--apply`.
- Python 3 standard library only. No dependencies, no client secret, no tokens saved to disk.

## Use it with Claude (as a skill)

This repo is a [Claude skill](https://docs.claude.com). Put the whole folder in your skills directory:

```bash
git clone https://github.com/itslmymy/spotify-liked-by-year ~/.claude/skills/spotify-liked-by-year
```

Then ask Claude: "Group my Spotify liked songs by the year I liked them." Claude will walk you through the setup below. In Claude's web or desktop app you can instead zip this folder and upload it on the Skills settings page.

## Use it on its own (just the script)

### 1. Create a Spotify app (one time)

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) and log in.
2. Click **Create app**.
3. Fill in:
   - **App name:** `Liked Songs by Year Saved` (Spotify doesn't allow "Spotify" in app names)
   - **Redirect URI:** `http://127.0.0.1:8888/callback` then click **Add**
   - **API:** tick **Web API**
4. Accept the terms and save.
5. Open **Settings** and copy your **Client ID**. You do not need the Client Secret.

Spotify apps in development mode may require a Premium account, and only you (and users you add) can use your app. Each person needs their own app.

### 2. Preview

```bash
python3 scripts/spotify_liked_by_year.py YOUR_CLIENT_ID
```

A browser tab opens so you can approve access. You'll see something like:

```
1592 liked songs in total:
  2023: 199 songs
  2024: 369 songs
  ...
```

Nothing has been changed yet.

### 3. Create the playlists

```bash
python3 scripts/spotify_liked_by_year.py YOUR_CLIENT_ID --apply
```

## Notes and limits

- Playlists are created **private**. Change them to public in Spotify if you like.
- Local files can't be added to playlists through the Spotify API and are skipped.
- Running `--apply` twice creates duplicate playlists; it doesn't merge into existing ones. If a run fails partway, the script lists what it created; delete any incomplete `Liked YYYY` playlist before retrying.
- Each run re-reads all your Liked Songs, so `--apply` counts include anything you liked since the dry run.
- If you get an HTTP 403 error: in the Developer Dashboard, open your app, go to **Settings → User Management**, and add your own Spotify account email.
- The script waits up to 5 minutes for you to approve access in the browser.
- Permissions requested: read your library, and create/modify your playlists.

## License

MIT, see [LICENSE](LICENSE).
