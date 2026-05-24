# llabench

Curated LLM benchmark database for Qwen3.6-35B-A3B on GB10 (DGX Spark), RTX 3090, and other devices.

## Structure

```
llabench/
├── index.html           # Interactive web interface (filter/search/sort)
├── data/
│   ├── benchmarks.json  # Structured benchmark database (machine-readable)
│   └── hardware.json    # Device definitions referenced by benchmarks
├── llabench.py          # Benchmark runner script (writes to benchmarks.json)
└── README.md
```

## Web Interface

Open `index.html` in a browser to explore benchmarks with filters, search, and sorting. Filter selections and sort order persist in localStorage across page refreshes.

Deploy as static site: serve `index.html` from any HTTP server or enable GitHub Pages.

## Benchmark Schema

Each entry in `data/benchmarks.json` includes:

- **id**: unique identifier
- **hardware_id**: reference key into `data/hardware.json`
- **source**: `"own-run"` or `"external"`
- **source_url**: link to source (blog, repo, model card)
- **device**: resolved from hardware.json — name, GPU, compute capability, memory bandwidth, unified memory
- **engine**: name, version, fork + URL, config flags
- **model**: name, quantization, total/active params, MTP flag
- **test**: context size (actual tested), concurrency, prompt TPS, gen TPS, avg completion tokens, rounds, notes

New entries can be added manually or via `llabench.py`.

## Quick Start (CLI)

```bash
# Run benchmark (slot 1, 10 rounds, with MTP)
python3 llabench.py --slot 1 --rounds 10

# Run without MTP (baseline)
python3 llabench.py --slot 1 --rounds 10 --no-mtp

# Use different prompt
python3 llabench.py --slot 1 --rounds 10 --prompt code
```

Output is appended to `data/benchmarks.json` under `source: "own-run"`.

## Current Results

**Key finding:** GB10 is memory-bandwidth bound at 273 GB/s. Theoretical ceiling ~91 tok/s single-stream, real-world realizes ~32% = 28-30 tok/s for FP8. NVFP4 projects ~55-60 tok/s.

**Our result:** ~53-54 tok/s on GB10 with MTP enabled — already near the projected NVFP4 ceiling.

## Hardware Comparison

| Hardware | Bandwidth | Unified Mem | Notes |
|----------|----------|-------------|-------|
| GB10 (DGX Spark) | 273 GB/s LPDDR5x | 128 GB | CPU-GPU unified |
| RTX 3090 | ~1000 GB/s GDDR6X | No | PCIe, 24 GB |

GB10 has ~4x less bandwidth than RTX 3090 — this is the dominant throughput factor.

## Data Sources

Community benchmarks sourced from public blog posts, model cards, and GitHub repos. Each entry includes a `source_url` for verification. Own-run entries are tagged with `source: "own-run"`.

## Future Work

- [ ] Context depth sweep (32K, 64K, 128K, 262K)
- [ ] KV cache quantization comparison (q8_0 vs f16 vs TurboQuant)
- [ ] Batch size tuning
- [ ] MTP n=2 vs n=3 comparison
- [ ] Quant comparison (NVFP4 vs Q4_K_XL on GB10)
- [ ] Baseline (no MTP) benchmark on GB10
