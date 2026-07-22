# Embedding the README demo video

GitHub **does not** render `<video src="docs/assets/prediction.mp4">` from files committed in the repository. The README sanitizer only allows inline players for assets on GitHub’s CDN (`github.com/user-attachments/assets/…` or `user-images.githubusercontent.com`).

The README uses an animated GIF preview (`docs/assets/prediction.gif`) that autoplays on the repo homepage, with a link to the full MP4 on GitHub’s blob viewer. For a **native inline MP4 player** directly in the README (no click-through), you must host the file on GitHub’s attachment CDN:

## Option A — GitHub web editor (fastest)

1. Open [`README.md`](https://github.com/lwan1/movienet-scene-segmentation/edit/main/README.md) on GitHub and click **Edit**.
2. In the **Demo** section, delete the GIF line.
3. Drag `docs/assets/prediction.mp4` from your machine into the editor (or use **Attach files**).
4. GitHub uploads the file and inserts a `user-attachments` URL. Wrap it if needed:

   ```html
   <video src="https://github.com/user-attachments/assets/XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX" controls playsinline width="100%"></video>
   ```

5. Commit directly to `main`.

## Option B — Upload script

If you have your `user_session` cookie (DevTools → Application → Cookies → `github.com`):

```bash
export GITHUB_USER_SESSION="your_user_session_cookie"
python scripts/upload_readme_demo_video.py --update-readme
git add README.md && git commit -m "Embed README demo via GitHub CDN"
```

The script prints the CDN URL and can patch `README.md` automatically.
