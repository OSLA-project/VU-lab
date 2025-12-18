[![github repo badge](https://img.shields.io/badge/github-repo-000.svg?logo=github&labelColor=gray&color=blue)](https://github.com/OSLA-project/VU-lab) [![github license badge](https://img.shields.io/github/license/OSLA-project/VU-lab)](https://github.com/OSLA-project/VU-lab) [![workflow scq badge](https://sonarcloud.io/api/project_badges/measure?project=OSLA-project_VU-lab&metric=alert_status)](https://sonarcloud.io/dashboard?id=OSLA-project_VU-lab)  [![build](https://github.com/OSLA-project/VU-lab/actions/workflows/build.yml/badge.svg)](https://github.com/OSLA-project/VU-lab/actions/workflows/build.yml) [![Integration test](https://github.com/OSLA-project/VU-lab/actions/workflows/test-compose.yml/badge.svg)](https://github.com/OSLA-project/VU-lab/actions/workflows/test-compose.yml)

Configuration of openlab for VU lab

This repo integrates the following SiLa connectors:
- [teleshake](https://gitlab.com/sila-driver-group/teleshake)
- Gen5 (private connector)
- [Generic robot arm](https://gitlab.com/OpenLabAutomation/device-integration/genericroboticarm)

## Prerequisites
In order to use this setup, you will need to have the following prerequisites installed:
- Either [[docker desktop](https://docs.docker.com/get-started/get-docker/) or [docker engine](https://docs.docker.com/engine/install/)

## How to use
To use this package, you should first clone it from github
```shell
git clone https://github.com/OSLA-project/VU-lab.git
```
## Prepare environment
There are a couple of parameters that need to be tuned, depending on your operating system, and whether you need to run 
in simulation mode or with real hardware. Three different scenarios have been prepared: you're running on Linux with simulated
hardware, or on Windows, with either simulated or real hardware.

Depending on your situation, you need to copy one of the following files to `.env` in the root of the repository:
- `.env.linux.simulated` (Linux with simulated hardware)
- `.env.windows.simulated` (Windows with simulated hardware)
- `.env.windows` (Windows with real hardware)

## Running the services
Use the following command to start all sila servers and the universal sila client: 

```shell
docker compose up
```

You can reach the services at the following addresses:
- [Sila Browser](http://localhost:3000)
- [Orchestrator webinterface](http://localhost:8050)
- [Robot arm webinterface](http://localhost:8055)]
- [Platform status db](http://localhost:8000)


## Credits

This package was created with [Copier](https://github.com/copier-org/copier) and the [NLeSC/python-template](https://github.com/NLeSC/python-template).
