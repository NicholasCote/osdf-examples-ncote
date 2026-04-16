#!/usr/bin/env python3
"""
Audit notebook imports across a repository.

Walks every .ipynb file, extracts top-level imports from code cells, filters out
stdlib and local modules, maps import names to their actual distribution package
names (cv2 -> opencv, PIL -> pillow, etc.), and emits:

  - imports.json         raw SBOM: per-notebook and aggregated imports
  - environment.yml      ready-to-use conda env file
  - requirements.txt     pip-compatible list (loose, no version pins)
  - summary.txt          human-readable overview

Intended for atmospheric/climate science repos but generalizes fine.
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from collections import defaultdict
from pathlib import Path

import nbformat
from stdlib_list import stdlib_list


# Import name -> package name on PyPI / conda-forge.
# Only includes cases where the import name diverges from the install name.
# Biased toward scientific Python / geoscience because that's the audience.
IMPORT_TO_PACKAGE = {
    "cv2": "opencv",
    "PIL": "pillow",
    "sklearn": "scikit-learn",
    "skimage": "scikit-image",
    "yaml": "pyyaml",
    "bs4": "beautifulsoup4",
    "dateutil": "python-dateutil",
    "dotenv": "python-dotenv",
    "serial": "pyserial",
    "Crypto": "pycryptodome",
    "OpenSSL": "pyopenssl",
    "pkg_resources": "setuptools",
    "mpl_toolkits": "matplotlib",
    "netCDF4": "netcdf4",
    "osgeo": "gdal",
    "tables": "pytables",
    "ecmwflibs": "ecmwflibs",
    "cfgrib": "cfgrib",
    "google": "google-cloud-storage",  # ambiguous; user may need to adjust
    "grpc": "grpcio",
    "mpi4py": "mpi4py",
    "IPython": "ipython",
    "notebook": "notebook",
    "jupyter_server": "jupyter-server",
}

# Packages that should be pinned via conda-forge even when a PyPI equivalent exists,
# because the conda build is significantly better (binary deps, C libs, etc.).
PREFER_CONDA_FORGE = {
    "numpy", "scipy", "pandas", "xarray", "netcdf4", "h5py", "h5netcdf",
    "matplotlib", "cartopy", "gdal", "rasterio", "fiona", "shapely",
    "pyproj", "geopandas", "pyart", "metpy", "siphon", "cfgrib",
    "eccodes", "esmpy", "xesmf", "dask", "distributed", "zarr",
    "numcodecs", "pytables", "bottleneck", "numba", "llvmlite",
    "opencv", "pillow", "scikit-learn", "scikit-image",
    "geocat-comp", "geocat-viz", "geocat-datafiles",
    "intake", "intake-esm", "kerchunk", "fsspec", "s3fs", "gcsfs",
    "nc-time-axis", "cftime", "udunits2",
}

# Known pip-only packages in the geoscience ecosystem.
PIP_ONLY = {
    "aiowebdav", "pelicanfs", "fastlite",
}


def collect_stdlib(py_version: str) -> set[str]:
    """Build a stdlib set covering the target Python version and common ancestors."""
    std: set[str] = set()
    for v in {py_version, "3.10", "3.11", "3.12"}:
        try:
            std.update(stdlib_list(v))
        except Exception:
            continue
    # Always-safe additions
    std.update({"__future__", "typing_extensions"})
    return std


def extract_imports(src: str) -> set[str]:
    """Return top-level module names imported by a block of Python source."""
    mods: set[str] = set()
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return mods
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mods.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            # Skip relative imports (level > 0)
            if node.level and node.level > 0:
                continue
            if node.module:
                mods.add(node.module.split(".")[0])
    return mods


def scan_notebook(path: Path) -> set[str]:
    """Extract import names from all code cells in a notebook."""
    imports: set[str] = set()
    try:
        nb = nbformat.read(path, as_version=4)
    except Exception as e:
        print(f"  ! failed to parse {path}: {e}", file=sys.stderr)
        return imports
    for cell in nb.cells:
        if cell.get("cell_type") != "code":
            continue
        src = cell.get("source", "")
        # Strip IPython magics/shell lines that break ast.parse
        lines = [
            ln for ln in src.splitlines()
            if not ln.lstrip().startswith(("%", "!", "?"))
        ]
        imports.update(extract_imports("\n".join(lines)))
    return imports


def find_local_modules(root: Path) -> set[str]:
    """Discover modules defined locally in the repo so they can be excluded."""
    local: set[str] = set()
    for p in root.rglob("*.py"):
        if any(part in {".git", ".venv", "venv", "node_modules"} for part in p.parts):
            continue
        local.add(p.stem)
        # Top-level package dirs
        if p.name == "__init__.py":
            local.add(p.parent.name)
    # Also top-level dirs that contain an __init__.py
    for p in root.iterdir():
        if p.is_dir() and (p / "__init__.py").exists():
            local.add(p.name)
    return local


def resolve_package(import_name: str) -> str:
    """Map an import name to its installable package name."""
    return IMPORT_TO_PACKAGE.get(import_name, import_name).lower()


def classify(pkg: str) -> str:
    """Return 'conda' for conda-forge preferred, 'pip' for pip-only, else 'conda' as default."""
    if pkg in PIP_ONLY:
        return "pip"
    if pkg in PREFER_CONDA_FORGE:
        return "conda"
    # Default to conda-forge; micromamba will fall back cleanly if not found,
    # but most scientific packages live there.
    return "conda"


def write_environment_yml(out: Path, conda_pkgs: list[str], pip_pkgs: list[str], py_version: str) -> None:
    lines = [
        "name: nb-env",
        "channels:",
        "  - conda-forge",
        "dependencies:",
        f"  - python={py_version}",
        "  - pip",
        "  - jupyter",
        "  - nbconvert",
        "  - ipykernel",
    ]
    for pkg in sorted(conda_pkgs):
        lines.append(f"  - {pkg}")
    if pip_pkgs:
        lines.append("  - pip:")
        for pkg in sorted(pip_pkgs):
            lines.append(f"      - {pkg}")
    out.write_text("\n".join(lines) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path("."))
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--target-python", default="3.11")
    args = ap.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    stdlib = collect_stdlib(args.target_python)
    local_mods = find_local_modules(args.root)

    skip_dirs = {".git", ".ipynb_checkpoints", "node_modules", ".venv", "venv"}
    notebooks = [
        p for p in args.root.rglob("*.ipynb")
        if not any(part in skip_dirs for part in p.parts)
    ]
    notebooks.sort()

    per_notebook: dict[str, list[str]] = {}
    all_imports: set[str] = set()
    import_to_notebooks: dict[str, list[str]] = defaultdict(list)

    print(f"Scanning {len(notebooks)} notebook(s)...")
    for nb in notebooks:
        rel = str(nb.relative_to(args.root))
        imports = scan_notebook(nb)
        # Filter stdlib, local modules, and private modules
        external = sorted(
            m for m in imports
            if m
            and not m.startswith("_")
            and m not in stdlib
            and m not in local_mods
        )
        per_notebook[rel] = external
        for m in external:
            import_to_notebooks[m].append(rel)
        all_imports.update(external)
        print(f"  {rel}: {len(external)} external imports")

    # Resolve to package names
    conda_pkgs: set[str] = set()
    pip_pkgs: set[str] = set()
    resolution: dict[str, dict] = {}
    for imp in sorted(all_imports):
        pkg = resolve_package(imp)
        channel = classify(pkg)
        resolution[imp] = {
            "package": pkg,
            "channel": channel,
            "used_by": import_to_notebooks[imp],
        }
        (pip_pkgs if channel == "pip" else conda_pkgs).add(pkg)

    # --- SBOM JSON
    sbom = {
        "target_python": args.target_python,
        "notebooks_scanned": len(notebooks),
        "unique_imports": len(all_imports),
        "per_notebook": per_notebook,
        "resolution": resolution,
        "conda_packages": sorted(conda_pkgs),
        "pip_packages": sorted(pip_pkgs),
    }
    (args.out_dir / "imports.json").write_text(json.dumps(sbom, indent=2))

    # --- environment.yml
    write_environment_yml(
        args.out_dir / "environment.yml",
        sorted(conda_pkgs),
        sorted(pip_pkgs),
        args.target_python,
    )

    # --- requirements.txt (loose, for reference / Binder pip fallback)
    all_pkgs = sorted(conda_pkgs | pip_pkgs)
    (args.out_dir / "requirements.txt").write_text("\n".join(all_pkgs) + "\n")

    # --- summary
    summary_lines = [
        f"Notebooks scanned: {len(notebooks)}",
        f"Unique external imports: {len(all_imports)}",
        f"Conda-forge packages: {len(conda_pkgs)}",
        f"Pip-only packages: {len(pip_pkgs)}",
        "",
        "Top imports by notebook count:",
    ]
    top = sorted(
        resolution.items(),
        key=lambda kv: (-len(kv[1]["used_by"]), kv[0]),
    )[:20]
    for imp, info in top:
        summary_lines.append(
            f"  {imp:30s} -> {info['package']:30s} ({info['channel']}, used in {len(info['used_by'])} nb)"
        )
    (args.out_dir / "summary.txt").write_text("\n".join(summary_lines) + "\n")

    print("\n" + "\n".join(summary_lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())