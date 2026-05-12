---
title: Other Computational Platforms
date: 2026-1-28
author: Harsha R. Hampapura
---

# Other Computational Platforms

This section demonstrates that OSDF + PelicanFS is not tied to any single HPC center — data streams wherever your compute runs.

## TACC Stampede3

[Stampede3](https://www.tacc.utexas.edu/systems/stampede3/) is a large-scale HPC system at the Texas Advanced Computing Center (TACC), available via an XSEDE/ACCESS allocation. The included notebook reproduces the CESM2 bias-correction workflow on Stampede3 to show portability across HPC centers.

## Jetstream2

[Jetstream2](https://jetstream-cloud.org/) is an NSF-funded cloud computing platform hosted at Indiana University. The Jetstream notebooks walk through:

1. Launching a JupyterLab instance on Jetstream2 via the Exosphere interface
2. Reproducing the CESM ocean heat content and CMIP6 GMST workflows in a cloud environment

A minimum **m3.medium** instance (8 vCPUs, 30 GB RAM) is recommended.

## Open Science Pool (OSPool)

The [OSPool](https://osg-htc.org/services/open_science_pool.html) provides opportunistic HPC capacity across a federation of campuses. Benchmark notebooks measure data access throughput from NCAR's origin when jobs run on OSPool access points, including the dedicated AP40 node.

## Prerequisites

All platforms require a valid allocation or account on the respective resource. See each notebook's introduction cell for platform-specific setup instructions.