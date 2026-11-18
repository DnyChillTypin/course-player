# Course Player

A small local web viewer for a downloaded Coursera course: sidebar navigation, video player with subtitles and
clickable transcript, speed control, resume position, progress tracking, and in-page quizzes.

This repo contains only the viewer code. Course media is **not** included.

## Setup
1. Download the course with [dl_coursera](https://github.com/FLZ101/dl_coursera) so the course folder sits next to `site/`:
   ```
   coursera/
     <course-slug>/   (downloaded media)
     site/            (this repo)
   ```
2. Set the course folder name in `server.py` (`COURSE`) and `build.py` (`slug`).
3. `python build.py` to generate `manifest.json` (needs `<course-slug>/.cache/crawl.json`).
4. `python server.py 8000` (or run `start.bat`) and open http://127.0.0.1:8000.
