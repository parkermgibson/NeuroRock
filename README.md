# NeuroRock

Three musical-instrument brain–computer interfaces that play together as a band:

| Instrument | Controlled by | Signal |
|---|---|---|
| Drums | Muscle contractions (forearms, calves) | EMG |
| Bass | Relaxed alpha rhythm (eyes open / closed, calm focus) | EEG, 8–13 Hz |
| Guitar | Imagined hand / foot movement | EEG motor imagery |

Built by the UC Davis Neurotech Club for the California NeuroTech Conference. The clinical goal: give patients with
different motor and cognitive abilities a way to make music together.

Everything happens in one lightweight desktop app: signal check, calibration, and playing. The full plan is in
[docs/PLAN.md](docs/PLAN.md).

## Status

**Skeleton.** The app opens with its sidebar and six pages (Setup, Calibrate, Play, Session, Sound, Settings).
Each page says what it will do and which milestone brings it. Boards, sound and signal processing come next.

## Quick start (Windows)

You need [uv](https://docs.astral.sh/uv/) (`winget install astral-sh.uv`). It installs the right Python for you.

```bash
git clone <repo-url> NeuroRock
cd NeuroRock
uv sync
uv run neurorock
```

## Project layout

```
neurorock/
  app/         PySide6 GUI: main window, theme, pages
  boards/      signal sources (Cyton, simulated, replay) and the acquisition loop
  core/        shared types every part codes against
  pipelines/   signal in, musical intents out (EMG drums, alpha bass, MI guitar)
  recording/   session recording and musician profiles
  protocols/   guided calibration recordings
  music/       keys and scales, the band's clock, rhythm patterns, instrument parts
  sound/       the in-house low-delay sound engine
tests/         pytest suite, runs with no hardware
docs/          plan, hardware setup
```

## Development

```bash
uv run pytest          # tests
uv run ruff check .    # lint
uv run ruff format .   # format
```
