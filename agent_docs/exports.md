# Exports

Every exporter takes a validated `Deck` and returns bytes (Google Slides returns a link). Exporters don't touch the database or look up the user; the API layer handles that and checks ownership before it calls one.

## PPTX (`exporters/pptx.py`)

- Uses python-pptx. Set the slide size to 16:9 (`Inches(13.333)` × `Inches(7.5)`). The default `Presentation()` is 4:3, which is what the prototype produced.
- One builder function per layout. Apply the theme's background, text color and font, and write `notes` into each slide's notes.
- Write to a `BytesIO` and stream it back with the MIME type `application/vnd.openxmlformats-officedocument.presentationml.presentation`. Nothing gets written into `data/` or anywhere else in the repo.

## PDF (`exporters/pdf.py`)

- Builds the PPTX first, then converts it with LibreOffice headless, so the PDF matches the PPTX: `soffice --headless --convert-to pdf --outdir <tmpdir> <file.pptx>`.
- The binary path comes from the `SOFFICE_PATH` env var. On Windows that's usually `C:\Program Files\LibreOffice\program\soffice.exe`, and in Docker it's `soffice`.
- Use a fresh temp dir for each request and a 60 s timeout. Pass `-env:UserInstallation=file:///<tmpdir>/lo_profile` so conversions running at the same time don't lock each other out.
- In the Docker image, install `libreoffice-impress` plus metric-compatible fonts (for example `fonts-crosextra-carlito` in place of Calibri). Without them the layout shifts.
- Tests that need `soffice` are marked so they're skipped when it isn't installed.

## Google Slides (`exporters/google_slides.py`)

- Sign-in asks only for `openid email profile`. The first time a user exports to Google Slides, request `https://www.googleapis.com/auth/drive.file` incrementally. That scope only covers files this app creates.
- Upload the PPTX with Drive v3 `files.create`, setting the metadata `mimeType` to `application/vnd.google-apps.presentation` so Drive converts it to Google Slides. Return the file's `webViewLink`.
- Store the refresh token encrypted in `oauth_accounts`. If it's revoked or expired, return `401 {"reconnect": "google"}` so the UI can ask the user to reconnect Google.
- While the Google OAuth app is in testing mode, only listed test users can sign in. Going public requires Google's app verification.
