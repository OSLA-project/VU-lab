# Plate Reader

**Hardware:** [Agilent BioTek Synergy HTX Multimode Reader](https://www.agilent.com/en/product/microplate-instrumentation/microplate-readers/multimode-microplate-readers/biotek-synergy-htx-multimode-reader-1623207)

**SiLA server source:** [`src/openlab_vu/platereader`](https://github.com/OSLA-project/VU-lab/tree/main/src/openlab_vu/platereader)

**Running mode:** Native under WSL (not in Docker — see below)

---

## Overview

{% include-markdown "../../src/openlab_vu/platereader/README.md" start="<!-- summary-start -->" end="<!-- summary-end -->" %}

Unlike the earlier Gen5-based setup, this connector does not talk to the reader through BioTek's Gen5 software. It drives the hardware directly using [PyLabRobot](https://github.com/PyLabRobot/pylabrobot)'s `SynergyHTBackend`, wrapped by `SynergyHTXController` in [`controller/synergy.py`](https://github.com/OSLA-project/VU-lab/tree/main/src/openlab_vu/platereader/controller/synergy.py). The SiLA feature implementation exposing this over the network lives in `synergy_htx/`.

---

## Running the SiLA server

The plate reader SiLA server runs natively under WSL rather than in Docker, because docker on windows does not allow for
connectivity with this device.

```bash
uv run python -m openlab_vu.platereader.synergy_htx --port 50052 --insecure
```

<!-- TODO: document USB passthrough steps for WSL (usbipd-win attach, device IDs, etc.) if applicable -->

---

## Configuration

| Environment variable / flag | Default | Description |
|---|---|---|
| `--port` | `50052` | SiLA2 server port |
| `--ip-address` | `127.0.0.1` (`0.0.0.0` in Docker) | Bind address |

See [`__main__.py`](https://github.com/OSLA-project/VU-lab/tree/main/src/openlab_vu/platereader/synergy_htx/__main__.py) for the full list of startup flags.
