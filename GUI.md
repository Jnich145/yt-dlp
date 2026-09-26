# GUI contribution in this fork

[yt_dlp_gui.py](yt_dlp_gui.py) is an experimental PyQt6 front end added by Justin Nichols. The underlying downloader is the upstream [yt-dlp project](https://github.com/yt-dlp/yt-dlp). This GUI is not an upstream release or a replacement for the upstream support channels and licensing terms.

## Local setup

Use a Python version supported by this checkout (see [pyproject.toml](pyproject.toml)) and a desktop environment capable of opening Qt windows.

```bash
git clone https://github.com/Jnich145/yt-dlp.git
cd yt-dlp
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e . PyQt6
python yt_dlp_gui.py
```

On Windows, use `.venv\Scripts\activate` to activate the environment. Install the FFmpeg executables separately when using merging, audio extraction, or conversion; upstream [dependency guidance](README.md#dependencies) explains their role.

Run from the repository root so the fallback stylesheet path resolves. [resources.py](resources.py) is a stub; [styles/style.qss](styles/style.qss) provides the fallback styling.

## What the code currently does

- Creates Basic, Advanced, and User Guide tabs.
- Loads available formats for a URL.
- Starts a download worker using the selected output path and supported options.
- Displays progress and completion/error text.

## Known limitations from source review

- Several displayed controls, including preferred video quality, subtitle settings, and the single-video toggle, are not read by `get_download_options`.
- The log-file option is explicitly a placeholder, and export fields do not have a corresponding export writer in the GUI.
- Format discovery runs synchronously in the UI thread and can stall the interface during a network request.
- The local downloader code is the version in this fork. Upstream download badges and releases below describe upstream, not a newly packaged GUI build.

This documentation update was checked against the source and local links. It does not claim a fresh desktop smoke test or successful download. Report GUI-specific issues to [this fork](https://github.com/Jnich145/yt-dlp/issues), with the revision, selected options, and error text.
