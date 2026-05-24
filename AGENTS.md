# llabench — Agent Guidelines

## Repo Structure

```
llabench/
├── index.html           # Single-file web UI (HTML + CSS + JS inline)
├── data/
│   ├── benchmarks.json  # Curated benchmark database (array of entries)
│   └── hardware.json    # Device definitions, referenced by benchmarks.json via hardware_id
├── llabench.py          # CLI runner — appends to benchmarks.json as "own-run"
└── README.md            # User-facing documentation
```

No build step. `index.html` is self-contained — serve directly or deploy as static site.

## Data Model

### benchmarks.json entries have these fields:
- `id` — unique string identifier (e.g. `"aeon-7-gb10-heretic-dflash-k15"`)
- `date` — ISO date string
- `source` — `"own-run"` or `"external"`
- `source_url` — link to source (blog, repo, model card) or null
- `hardware_id` — reference key into `data/hardware.json`
- `engine` — `{name, version, fork, fork_url, config}`
- `model` — `{name, quant, total_params, active_params, mtp}`
- `test` — `{context_size, concurrency, prompt_tokens, token_generation_speed_tps, prompt_processing_speed_tps, avg_completion_tokens, rounds, note}`
- `notes` — free-text for additional context (concurrency ramp data, acceptance rates, etc.)

### hardware.json entries have:
- `id` — unique key (e.g. `"gb10-spark"`, `"rtx-3090"`)
- `name`, `gpu`, `compute_cap`, `memory_bandwidth`, `unified_memory`

### Naming conventions:
- Benchmark IDs: `{source}-{device}-{model-short}-{variant}` — lowercase, hyphenated
- Source tags: `"own-run"` for our tests, `"external"` for community data
- Model names in entries use the **full HuggingFace name** (e.g. `"AEON-7/Qwen3.6-35B-A3B-heretic-NVFP4"`)
- The web UI normalizes model names via `normalizeModel()` — strips org prefix and parenthetical notes, groups Qwen/Nemotron variants by base name

### Data conventions:
- `token_generation_speed_tps` — for concurrent tests, this is **aggregate** throughput (total tokens / total time)
- Put concurrency ramp details in the `notes` field of the single-concurrency entry, not as separate entries
- `context_size` = actual tested context, not max supported
- `mtp: true` means native MTP (speculative decoding within the model); DFlash and other external drafter methods use `mtp: false`

## Web UI Quirks

- Filters + sort persist in `localStorage` under key `llabench-filters`
- `populateFilters()` must be called **before** restoring saved filter state from localStorage — otherwise the recreated `<option>` elements lose the restored values
- Model normalization groups variants: `"RedHatAI/Qwen3.6-35B-A3B-NVFP4 + MTP"` → `"Qwen3.6-35B-A3B"`
- Quant normalization maps: NVFP4 variants → `"NVFP4"`, etc. (see `normalizeQuant()`)

## Adding New Benchmark Data

1. Edit `data/benchmarks.json` directly — append to the array
2. Use a descriptive `id` following the naming convention
3. Set `source_url` so data is traceable
4. For concurrency ramp data: add one entry at the lowest concurrency, put other concurrency numbers in `notes`
5. Run `python3 -c "import json; d=json.load(open('data/benchmarks.json')); print(len(d))"` to verify count

## llabench.py

- Runs curl against llama.cpp server at `localhost:8008`
- Appends results to `data/benchmarks.json` with `source: "own-run"`
- Uses `id_slot: 1` in the API payload — all benchmarks run on slot 1
- Output model name is hardcoded — update if switching models

## Common Tasks

### Add a community benchmark
```python
# Append to benchmarks.json array with full entry dict
# Set source="external", set source_url, use hardware_id from hardware.json
```

### Fix web UI filter issue
- Check `populateFilters()` ordering relative to localStorage restore block in `init()`
- Filters must be populated before values are restored

### Update hardware definitions
- Edit `data/hardware.json` — add new device entries with unique `id` keys
- Existing benchmarks reference by `hardware_id`, not inline device data
