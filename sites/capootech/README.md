# CapooTech Landing Page

This directory is the source of truth for `https://capoo.tech` static landing assets.

## Structure

- `index.html`: landing page entry
- `styles.css`: landing page stylesheet
- `lang-toggle.js`: language switch logic (default zh, toggle zh/en)
- `favicon-capoo.svg`: browser tab icon
- `images/capoo/*.webp`: gallery images

## Publish to HK server

1. Pick a release id, for example `20260208-1`.
2. Upload this folder to `/opt/sites/capootech/releases/<release_id>/`.
3. Update symlink: `/opt/sites/capootech/current -> /opt/sites/capootech/releases/<release_id>`.
4. Keep Nginx root and image alias pointed to `/opt/sites/capootech/current`.
5. Run `nginx -t && systemctl reload nginx`.

## Rollback

Point `current` symlink back to previous release and reload Nginx.
