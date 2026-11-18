# Course Player

A local web viewer for courses downloaded with [dl_coursera](https://github.com/FLZ101/dl_coursera): a course
library, sidebar navigation, video player with subtitles and a clickable transcript, speed control, resume
position, per-course progress tracking, and in-page quizzes. Supports any number of courses.

This repo contains only the viewer. Course media is **not** included: each `courses/<course-slug>/` folder is
kept as an empty placeholder (`.gitkeep`) and its contents are git-ignored.

## Add a course
```
dl_coursera --cookies cookies.txt --outdir courses --quiz <course-slug>
```
or copy an existing dl_coursera output folder to `courses/<course-slug>/` (it must contain `.cache/crawl.json`).

## Run
```
python server.py 8000      # or double-click start.bat
```
Open http://127.0.0.1:8000. The library rescans `courses/` every time you open it, so new courses appear on refresh.
Requires Python 3.8+ and no extra packages. Progress is stored in your browser's localStorage, per course.
