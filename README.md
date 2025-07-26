For livekit dependencies, run:
```bash
uv pip install \
              "livekit-agents[openai,sarvam,elevenlabs,silero,turn-detector]~=1.0" \
              "livekit-plugins-noise-cancellation~=0.2" \
              "python-dotenv"```
```
```bash
python main.py download-files
```

For running the local console:

```bash
python main.py console
```

For running in dev mode:


```bash
python main.py dev
```

For running in prod mode:

```bash
python main.py start
```