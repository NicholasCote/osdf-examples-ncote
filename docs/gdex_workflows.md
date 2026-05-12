---
title: GDEX workflows
date: 2026-1-28
author: Harsha R. Hampapura
---

# NCAR HPC Workflows

These notebooks are designed to be executed on **NCAR's HPC system Casper** and demonstrate how to stream geoscience data via OSDF directly into memory — no local download required.

## NCAR Data Origin

Notebooks in this section access datasets hosted on [NCAR's Geoscience Data Exchange (GDEX)](https://gdex.ucar.edu/) through NCAR's OSDF origin server. Datasets include:

- **CESM2 LENS** — Large Ensemble Community Earth System Model output (surface temperature, ocean heat content, global mean surface temperature)
- **DART/CAM6** — Data Assimilation Research Testbed reanalysis
- **JRA-3Q** — Japanese Reanalysis dataset
- **ERA5 / EOL ERA5** — ECMWF Reanalysis fifth generation via NCAR/EOL
- **NA-CORDEX** — North American CORDEX regional climate projections
- **CONUS404** — High-resolution CONUS analysis at 4 km / 404 variables
- **SAAG** — Southern Ocean Aerosol and Chemistry dataset
- **HadISST** — Hadley Centre sea ice and SST observations

## Other Data Origins

These notebooks access publicly available datasets from external OSDF origins (primarily the AWS Open Data program) using the same PelicanFS streaming approach:

- **CMIP6 (zarr)** — Multi-model ensemble data (GMST, ECS, bias correction, precipitation)
- **HRRR** — High Resolution Rapid Refresh numerical weather model output

## ML Workflows

Machine learning examples built on top of OSDF-streamed training data:

- **Nino3.4 Index Prediction** — Logistic regression model to predict ENSO phase from sea surface temperatures
