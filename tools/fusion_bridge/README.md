# ClaudeBridge — run Python in the live Fusion GUI

A small Fusion add-in plus a client, used to build `design/cad_fusion_revB/` live in the Fusion window.

- `ClaudeBridge/` — the add-in. It listens on `127.0.0.1:8765` only and needs the random token it writes to
  `token.txt` (new on every start). Code runs on Fusion's main thread, so the model updates on screen as it is built.
- `fx.py` — client: `python fx.py script.py`, `python fx.py -c "print(app.version)"`, `python fx.py --ping`.

## Install

1. Copy `ClaudeBridge/` to `%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\`.
2. In Fusion: open a design, press **Shift+S** → **Add-Ins** → ClaudeBridge → **Run** (tick *Run on Startup* to keep it).
3. `python fx.py --ping` should answer `pong`.

Stop it from the same dialog when you are done: while it runs, any program on this computer that can read your
`%APPDATA%` can send code to Fusion.
