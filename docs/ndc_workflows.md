---
title: NDC workflows
author: Harsha R. Hampapura
date: 2026-1-28
---

# NDC Workflows

This section contains workflows developed as part of the [National Discovery Cloud (NDC)](https://ndc-pathfinders.org/) pathfinder initiative. Most of these notebooks can be run on a **laptop or personal device** without access to an HPC system.

## Workflows

- **AWS Benchmark** — Measures data access throughput for CESM2 LENS data served from the AWS Open Data origin, across various chunk sizes.
- **NCAR Origin Benchmark** — Equivalent benchmark against NCAR's own OSDF origin; includes a variant targeting OSPool access point AP40.
- **Envistor AP40 Test** — Exercises the AP40 access point from the OSPool environment.
- **Spectral Change Detection** — Uses Sentinel-2 satellite imagery from AWS to detect vegetation or land-cover change via spectral indices.
- **SONAR AI** — Loads NOAA water-column sonar data from AWS and generates echogram visualizations.

## Getting Started

No HPC allocation is required. Install the environment from `requirements.txt` or `environment.yml` and launch JupyterLab locally:

```bash
conda env create -f environment.yml
conda activate nb-env
jupyter lab
```

