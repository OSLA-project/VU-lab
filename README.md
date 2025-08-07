## Badges

(Customize these badges with your own links, and check https://shields.io/ or https://badgen.net/ to see which other badges are available.)

| fair-software.eu recommendations | |
| :-- | :--  |
| (1/5) code repository              | [![github repo badge](https://img.shields.io/badge/github-repo-000.svg?logo=github&labelColor=gray&color=blue)](https://github.com/OSLA-project/VU-lab) |
| (2/5) license                      | [![github license badge](https://img.shields.io/github/license/OSLA-project/VU-lab)](https://github.com/OSLA-project/VU-lab) |
| (3/5) community registry           | [![RSD](https://img.shields.io/badge/rsd-openlab_vu-00a3e3.svg)](https://www.research-software.nl/software/openlab_vu) [![workflow pypi badge](https://img.shields.io/pypi/v/openlab_vu.svg?colorB=blue)](https://pypi.python.org/project/openlab_vu/) |
| (4/5) citation                     | [![DOI](https://zenodo.org/badge/DOI/<replace-with-created-DOI>.svg)](https://doi.org/<replace-with-created-DOI>)|
| (5/5) checklist                    | [![workflow cii badge](https://bestpractices.coreinfrastructure.org/projects/<replace-with-created-project-identifier>/badge)](https://bestpractices.coreinfrastructure.org/projects/<replace-with-created-project-identifier>) |
| howfairis                          | [![fair-software badge](https://img.shields.io/badge/fair--software.eu-%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8B-yellow)](https://fair-software.eu) |
| **Other best practices**           | &nbsp; |
| Static analysis                    | [![workflow scq badge](https://sonarcloud.io/api/project_badges/measure?project=OSLA-project_openlab_vu&metric=alert_status)](https://sonarcloud.io/dashboard?id=OSLA-project_openlab_vu) |
| Coverage                           | [![workflow scc badge](https://sonarcloud.io/api/project_badges/measure?project=OSLA-project_openlab_vu&metric=coverage)](https://sonarcloud.io/dashboard?id=OSLA-project_openlab_vu) || **GitHub Actions**                 | &nbsp; |
| Build                              | [![build](https://github.com/OSLA-project/openlab_vu/actions/workflows/build.yml/badge.svg)](https://github.com/OSLA-project/openlab_vu/actions/workflows/build.yml) |
| Citation data consistency          | [![cffconvert](https://github.com/OSLA-project/openlab_vu/actions/workflows/cffconvert.yml/badge.svg)](https://github.com/OSLA-project/openlab_vu/actions/workflows/cffconvert.yml) || SonarCloud                         | [![sonarcloud](https://github.com/OSLA-project/openlab_vu/actions/workflows/sonarcloud.yml/badge.svg)](https://github.com/OSLA-project/openlab_vu/actions/workflows/sonarcloud.yml) |## How to use openlab_vu

Configuration of openlab for VU lab

The project setup is documented in [project_setup.md](project_setup.md). Feel free to remove this document (and/or the link to this document) if you don't need it.

This repo integrates the following SiLa connectors:
- [teleshake](https://gitlab.com/sila-driver-group/teleshake)
- Gen5 (private connector)
- [Generic robot arm](https://gitlab.com/OpenLabAutomation/device-integration/genericroboticarm)

## Installation

To install openlab_vu from GitHub repository, do:

```console
git clone git@github.com:OSLA-project/openlab_vu.git
cd openlab_vu
python -m pip install .
```

## Documentation

Include a link to your project's full documentation here.

## Contributing

If you want to contribute to the development of openlab_vu,
have a look at the [contribution guidelines](CONTRIBUTING.md).

## Credits

This package was created with [Copier](https://github.com/copier-org/copier) and the [NLeSC/python-template](https://github.com/NLeSC/python-template).
