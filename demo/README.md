# Demo Recording Assets

Use the paced terminal script for the final screen recording:

```bash
./scripts/99_record_demo.sh
```

For a one-minute terminal recording pass, shorten the pauses:

```bash
env DEMO_SHORT_PAUSE=2 DEMO_MEDIUM_PAUSE=4 DEMO_LONG_PAUSE=10 ./scripts/99_record_demo.sh
```

Use `demo/demo_subtitles_final.srt` as the English subtitle track. It is written
so judges can understand the project without voice narration.

The default recording pace is tuned for roughly 3:00, matching the final SRT.

If the recording starts with extra dead time before the script appears, shift the
SRT timings by that offset before uploading to YouTube.

For a polished silent pitch video generated from repository context:

```bash
python scripts/97_make_pitch_video.py
```

It writes a 1920x1080 MP4 and matching SRT file under `demo/generated/`. That
folder is ignored by git because the files are submission artifacts, not source.

For the final combined submission video:

```bash
python scripts/96_make_final_submission_video.py
```

This creates a hard-captioned 3-minute MP4: roughly 2 minutes of pitch slides
followed by 1 minute of terminal execution evidence from the earlier recording.
By default it also copies the upload-ready file to the Desktop.
