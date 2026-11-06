# NeuroRock Build Plan

Three musical-instrument BCIs (EMG drums, alpha-wave bass, motor-imagery guitar) that play together as a band.
Everything happens inside one app: signal check, calibration, and playing. The app stays deliberately lightweight:
no separate research or analysis tooling.

_Last updated 2026-11-04._

---

## 1. Decisions

| Area | Decision |
|---|---|
| Language | Python 3.12 |
| GUI | PySide6 + pyqtgraph |
| Hardware | OpenBCI Cyton (8 ch, 250 Hz), one per musician, through BrainFlow |
| Laptops | Windows first; the code also runs on Mac |
| Band sync | MQTT (Mosquitto broker). One running copy of the app per instrument, on one machine or many |
| Timing | The conductor announces tempo + start time once; every copy computes the beat grid itself and corrects for clock differences |
| Sound | In-house engine in its own process (main path) + MIDI out (option). Same event stream feeds both |
| Effects | Spotify `pedalboard` (GPL-3, so NeuroRock is open source) |
| Drums | Live and snap-to-beat, with adjustable snap strength |
| Guitar mapping | Open. Start with 2 classes (left/right hand) = step down/up the scale, rest = hold |
| Who drives the GUI | A helper. Accessibility (eye tracking, SSVEP) later |
| Data collection | Calibration recordings in the app (Calibrate page); no research mode, no PsychoPy/LSL |
| Code reuse | Adapt parts of PyBCI (MIT license, keep its copyright notice) — see section 7 |
| Guitar classifier | PyBCI's Riemannian tangent-space + shrinkage LDA (no CSP needed); filter 8–30 Hz before it |

---

## 2. How the app is put together

```
┌──────────────────────── main process ────────────────────────┐      ┌──── audio process ────┐
│                                                              │      │                       │
│  Board ──chunks──► Pipeline ──intents──► Music ──events──────┼─────►│ Scheduler             │
│  (Cyton/fake/     (EMG/alpha/MI)        (transport, rhythm,  │ queue│  → Voices             │
│   replay/keys)          │                scale, snap)        │      │  → Effects (pedalboard)│
│        │                │                    │               │      │  → Master → speakers  │
│        ▼                ▼                    ▼               │      └───────────────────────┘
│    Recorder        Calibration          Sync (MQTT) ◄────────┼──► other band members
│                                              │               │
│  GUI (PySide6) — shows and controls all of the above         │──► MIDI out (optional)
└──────────────────────────────────────────────────────────────┘
```

**Why two processes:** the audio process does nothing but make sound, so a busy GUI or a slow classifier can never
cause a click or dropout.

---

## 3. The contracts everyone codes against

These let the EMG team, the EEG team, and GUI/sound work at the same time without stepping on each other.
They live in `neurorock/core/types.py` and `neurorock/boards/base.py`; read those for the details.

| Type | What it is |
|---|---|
| `BoardSpec` | A board's name, sample rate, channel names and kinds (EEG / EMG / unused). Samples are always µV |
| `Board` | `start()`, `read() -> BoardRead`, `stop()`, `insert_marker(label)`. Only the acquisition thread reads |
| `Chunk` | What subscribers get: `first_sample` (absolute index), `data` (channels x samples, float32 µV), `markers`, `lost_before` |
| `Marker` | A label pinned to one absolute sample (`cue/left`, `hit/R-forearm/0.8`, ...) |
| `Intent` | What a pipeline outputs: instrument, sample, value (pad / scale step / class), strength |
| `NoteEvent` | What the music layer sends to the audio engine and MIDI out: time, instrument, note, velocity |

Rules of the road:

- Pipelines and the recorder **subscribe** to `Acquisition`; nobody else calls `board.read()`.
- Sample numbers are absolute. Lost samples still use up numbers, so a jump in `first_sample` is a gap; reset
  filters there.
- A pipeline module has `fit_calibration(session) -> calibration` (saved as JSON in the musician's profile,
  `data/<musician>/profile/`) and a class built from `(BoardSpec, calibration)` whose `process(chunk) -> list[Intent]`
  runs on the acquisition thread. The fit replays the recording through the same live code, so the levels it
  measures are the ones the live pipeline sees. `pipelines/emg_drums.py` is the reference.

---

## 4. In-app features (pages)

| Page | What the helper does there |
|---|---|
| **Session** | Pick the musician and instrument; start alone or join the band (broker address, conductor or member) |
| **Setup** | Connect the Cyton, live signal traces + spectrum, flag flat/railed channels, impedance check, electrode-placement diagram per instrument |
| **Calibrate** | Pick musician + instrument, press Start, follow the cues (see 5). Shows when each calibration was last done; later also fits the thresholds/model and shows how well it worked |
| **Play** | Big note display, beat light, what the classifier "sees", band status |
| **Sound** | Instrument, samples, envelopes, crossfade/glide, effects chain, key/scale/progression |
| **Settings** | Audio device + buffer size, latency meter, MIDI out, MQTT, data folder |

Each musician has a **profile** folder holding their calibrations, models, and preferences.

---

## 5. Calibrations

Calibrations are small YAML files in `neurorock/protocols/library/` (blocks, cues, durations, trial counts,
randomization), so they can be adjusted without touching code. Each one is a guided recording plus a "fit" step
(the fit arrives with each instrument's pipeline).

| Protocol | Cues | Length | Produces |
|---|---|---|---|
| `emg_calibration` | relax 5 s → hardest hit ×5 → softest hit ×5, per limb | ~1 min | Hit threshold + velocity range per limb |
| `alpha_calibration` | eyes open 30 s / eyes closed 30 s, ×2 (audio cues) | ~2 min | Personal alpha range → bin edges |
| `mi_training` | fixation 2 s → arrow cue → 4 s imagery → rest, ~40 trials per class, randomized | 10–15 min | Labeled trials → Riemannian + LDA model |
| `mi_topup` | same, 10 trials per class | ~3 min | Adapts the existing model |

---

## 6. Recording format

One folder per session, written as it records, so a crash never loses a whole session:

```
data/<musician>/<YYYY-MM-DD>_<protocol>_<nn>/
├── signal.f32        # raw float32 samples, appended live (channels interleaved)
├── events.jsonl      # one line per marker/cue/intent/note: {"sample": 12345, "t": 49.38, "label": "cue/left"}
└── session.json      # sfreq, channels, montage, board, musician, protocol, app version, notes
```

`neurorock.recording.load_session(path)` returns an MNE `Raw` with the events as annotations, so the notebooks and the
Calibrate page read the same thing. Saved sessions can also be replayed through the app as a fake board.

---

## 7. What we take from PyBCI

PyBCI is MIT licensed: copied files keep its copyright line (`Copyright (c) 2026 Prithviraj Mody`) in a header comment,
and `THIRD_PARTY_NOTICES.md` lists them. Paths below are relative to `PyBCI/apps/desktop/src` unless noted.
PyBCI is PyQt5; copied Qt code gets ported to PySide6 (`pyqtSignal` → `Signal`, fully scoped enums, `exec()`).

### Copy (almost as-is or with light stripping)

| PyBCI file | Becomes | Changes |
|---|---|---|
| `packages/pybci-sdk/.../hardware.py` | `core/hardware.py` | Drop the plugin base class; chunks as numpy arrays instead of lists |
| `backend/acquisition_backend.py` | `boards/session.py` | Drop the plugin registry; becomes the input to the single acquisition thread |
| `core_plugins/mock_hardware/*` | `boards/fake.py` | Pace output to real time |
| `core_plugins/simulated_bci_hardware/*` + `backend/training/signal_model.py` | `boards/simulated.py` | Add "eyes closed" (O1/O2 alpha up) and EMG-burst profiles. Gives realistic cue-driven fake signal for every instrument |
| `backend/streaming_filter.py` | `pipelines/filters.py` | Replace its pydantic `FilterStep` with a dataclass (~30 lines). Same filter code runs live and offline |
| `backend/decoder/{riemann,head,base,adapter,decoder}.py` | `training/decoder/` | Write a small `__init__`; strip the trust/signing parts of the model file format |
| `backend/training/calibration.py` (lines ~1–512, 705–736) | `training/fit.py` | Inline two small helpers. Keeps the trial-grouped cross-validation and the "better than chance" acceptance check |
| `backend/training/capture.py` | `recording/capture.py` | Sample-aligned cue markers and gap handling, writing into our session format |
| `backend/pipeline_graph/command_smoothing.py` | `pipelines/smoothing.py` | As-is. Hysteresis + dwell so the guitar/bass don't flicker between notes |
| `frontend/pages/record/stimulus_player.py` + `stimulus_window.py` | `protocols/player.py`, `app/cue_window.py` | Precise timers with absolute deadlines; markers go into the board stream |
| `frontend/pages/record/modes/preset_mode.py` (motor-imagery builder, ~125 lines) | `protocols/` | Turned into the `mi_training` YAML protocol |
| `core_plugins/midi_output/midi_output_plugin.py` | `sound/midi_out.py` | Dedicated MIDI thread instead of a timer per note |
| Tests: `FakeClock` + `ClockedPlugin` (from `test_live_stream_integrity.py`), `test_acquisition_backend.py`, `test_streaming_filter.py`, `test_decoder_riemann.py`, `test_training_calibration.py`, `fixtures/synthetic_raw.py` | `tests/` | Hardware-free tests that prove no samples are lost or repeated and that live = offline |

### Use as reference only

- `backend/pipeline_graph/executor.py` — `_LiveBuffer` and the live pacing loop (~200 lines): windows paced on the
  board's sample clock, catching up when behind. Rewrite it lean (no MNE object per window).
- `frontend/components/livestream_plot_stack.py` and the livestream page — ideas for the Setup page, but ours draws all
  channels in one plot with a rolling buffer.
- `backend/training/metrics.py` — lift `wolpaw_bits`, `confusion_matrix`, `channel_drift` for the Calibrate page's fit results.
- `backend/training/runner.py` — design notes on driving a session by sample clock instead of wall time.

### Don't copy (bugs found in review)

- The BrainFlow plugin always describes the synthetic board, so a real Cyton's 8 channels get silently dropped, and
  the setup form never passes a board ID. **PyBCI has never really run a Cyton.**
- The record page lets the plot and the recorder both drain the same buffer, so recordings have holes.
- Record-page markers use wall-clock time instead of sample position (jitter).
- The live plot keeps its whole history in growing Python lists.
- Windows COM-port detection is broken (use `serial.tools.list_ports`, FTDI vendor ID 0403).

### Not in PyBCI, so we build it

- Cyton configuration: channel on/off, gain, SRB2, and impedance (lead-off) checks
- Replay board for saved sessions
- One acquisition thread that fans data out to the plot, recorder, and pipeline
- EMG envelope + hit detection
- Alpha band power (O1/O2)
- Eyes-open/closed and EMG-strength protocols
- Everything musical: sound engine, music layer, band sync

---

## 8. Repo layout

```
neurorock/
├── neurorock/
│   ├── core/          # contracts (Chunk, Intent, NoteEvent...), band clock, config, logging
│   ├── boards/        # Cyton (BrainFlow), fake, replay, keyboard
│   ├── pipelines/     # emg_drums.py, alpha_bass.py, mi_guitar.py, shared filters
│   ├── music/         # transport, rhythm patterns, scales/progressions, snap-to-beat, instrument logic
│   ├── sound/         # audio process, scheduler, voices, SFZ loader, effects, master bus, MIDI out
│   ├── sync/          # MQTT client, topics, clock offset, conductor
│   ├── recording/     # recorder, session format, load_session
│   ├── protocols/     # calibration runner + library/*.yaml
│   ├── training/      # fit models from calibrations (M2/M4)
│   └── app/           # PySide6 main window + pages
├── tests/             # pytest, all runnable without hardware
├── docs/              # setup guides (incl. Cyton setup checklist)
└── pyproject.toml
```

---

## 9. Milestones

Calibration recording comes first (the guitar model needs several sessions of data), with the sound engine built
alongside.

### M0 — Skeleton (Nov 4–10)
- [x] Repo, `pyproject.toml`, `uv` environment, ruff, pytest, GitHub Actions running tests
- [x] Contracts in `core/` (starting from PyBCI's hardware contract); clock (band-clock sync comes in M3)
- [x] Boards: simulated (cue-driven, all three instruments), Cyton (new), replay (new), BrainFlow synthetic
- [x] Single acquisition thread fanning out to plot / recorder / pipeline
- [x] Main window + Setup page: connect, COM-port detection, dongle latency warning, live traces, spectrum,
      signal-quality table, markers, impedance check
- [x] Recorder writing the session format (PyBCI capture logic); `load_session`, `Session.to_mne()`
- [x] PyBCI's hardware-free test harness + streaming filter, with their tests
- [ ] **Still to do on hardware:** connect a real Cyton, confirm channel order, packet-loss detection and the
      impedance check (all written but untested without a board)
- **Done when:** a helper connects a Cyton (or the fake board), sees clean live signal, and records a session that loads in a notebook.

### M1 — Calibration + sound v1 (Nov 11–24)
- [x] Calibration runner (absolute deadlines, markers pinned to samples, beeps, practice run without a board,
      second-screen cues) + Calibrate page; the four calibrations above
- [x] Audio process: device selection (WASAPI first), WAV sample folders, built-in placeholder kits, envelopes,
      voice limits and choke groups with fades, sample-accurate scheduling, clock sync between processes
- [x] Transport (BPM, start/stop), rhythm patterns, key/scale mapping, metronome, drum snap-to-beat
- [x] Keyboard → intents → notes on the Play page, with a live note timeline
- [x] Latency meter (Settings), Sound page (levels, sample folders), restyled app
- [ ] **Still to check by ear:** listen on the club laptops; tune the placeholder sounds' levels
- **Done when:** calibrations record in-app, and the keyboard plays drums + bass in key, on the beat, with no clicks.

### M2 — EMG drums (Nov 25–Dec 12)
- [x] EMG pipeline: 20 Hz high-pass + notch → rectify → 30 Hz envelope → threshold with hysteresis and refractory
      → peak in the first 12 ms → log-scale velocity (soft hit ≈ 0.3, hard hit = 1.0)
- [x] `emg_calibration` fit step: runs when the calibration finishes; per-limb threshold, velocity range, and a
      grade with advice (missed hits, false hits, no signal); live and snap-to-beat modes (snap from M1)
- [x] Play page: start/stop EMG drums, level meter and pad per limb, sensitivity; simulated board answers
      calibration prompts and keyboard "flexes" so the whole path is testable without hardware
- [ ] **Still to check on a person:** real Cyton + electrodes: thresholds, crosstalk between limbs, drift as
      skin and electrodes warm up, and the felt delay (simulated: ~29 ms hard / ~38 ms soft from burst to hit,
      plus the sound card's output delay)
- **Done when:** flexing plays the right drum at a matching volume, live or snapped.

### M3 — Band mode + sound v2 (Winter, by Jan 31)
- [ ] MQTT sync: conductor, clock offset, shared tempo/key/progression, band status
- [ ] SFZ loading, multi-velocity + round-robin, choke groups, crossfade and glide modes
- [ ] Effects chain + cabinet IRs, master compressor/limiter
- [ ] MIDI out
- **Done when:** two Windows laptops play together in time and it sounds like a band.

### M4 — Alpha bass + MI guitar (by Feb 15)
- [ ] Alpha pipeline + calibration fit + bins → scale steps (test bin layouts on recorded data)
- [ ] MI pipeline: PyBCI's Riemannian decoder + fit/acceptance check; Calibrate page shows cross-validated accuracy
- [ ] Sliding-window classification (paced on the sample clock), smoothed, most recent class played on each beat
- **Done when:** both EEG instruments play musically on a real musician.

### M5 — Practice and polish (Feb 15 → CNTC, Apr 26)
- [ ] Weekly practice sessions recorded for accuracy-over-time results
- [ ] PyInstaller `.exe` for helpers; setup guide
- [ ] Accessibility options; fixes from practice

---

## 10. Who builds what

| Area | Owner (suggested) |
|---|---|
| App shell, pages, sound engine, sync, music layer | GUI & Sound Design (Vadim) |
| EMG pipeline + `emg_calibration` | EMG team |
| Alpha + MI pipelines, calibration content and fit steps | EEG team + Producers |
| Electrode placement guides, protocol content, accuracy metrics | Research & UX (Producers) |
| Hardware, purchases, practice schedule | Logistics (Parker) |

Pipelines only touch `pipelines/` and `protocols/`, against the contracts in section 3.

---

## 11. Risks

| Risk | Plan |
|---|---|
| Python audio glitches | Separate audio process; small fixed buffers; numba or compiled core if needed |
| Campus Wi-Fi blocks band sync | Dedicated travel router or phone hotspot |
| MI accuracy too low | Two classes first; more training sessions; smoothing; scale-step mapping keeps wrong guesses musical |
| PyBCI never ran a real Cyton | Our Cyton board is new code, tested against real hardware in M0, not copied |
| Cyton data arrives in bunches | FTDI latency timer fix (docs/cyton-setup.md) |
| Electrodes not bought yet (EMG) | M2 can start on recorded/fake EMG; purchase ASAP |
