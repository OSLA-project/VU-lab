# Gen5 Sila connector
This directory contains the Dockerfile for the Gen5 Sila connector. However, the connector itself is
private and not available in this repository. If you have access to the Gen5 Sila codebase, you can
copy the folder to the `gen5` subdirectory and build the Docker image using the provided Dockerfile.

Directory structure:
```
VU-lab/
├── gen5/
│   ├── Dockerfile
│   ├── README.md
│   └── gen5/
│       ├── ... (Gen5 Sila connector code)
|── ... (other files)
``` 

One change has to be made to the gen5 codebase though. The unitelabs-cdk is fixed to an older version that is incompatible
with the rest of the codebase. To fix this, delete the version of unitelabs-cdk in `gen5/gen5/pyproject.toml` and replace it with:

```toml
unitelabs-cdk = {source = "unitelabs"}
```