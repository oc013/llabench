# External Benchmarks — GB10 / RTX 3090 Community Data

## Sources

- rikkarth.com — Qwen3.6-35B-A3B-FP8 on GB10 via vLLM (2026-04-23)
- HackMD (thc1006) — Every llama.cpp spec-decode mode on Qwen3.6-35B-A3B + RTX 3090 (2026-04-22)
- carteakey.dev — Running Qwen3.6-35B-A3B MTP locally on 12GB VRAM (2026-05-12)
- eugr/spark-vllm-docker — DGX Spark vLLM + DFlash (2026-05-06)
- JetsonHacks — llama.cpp on NVIDIA DGX Spark benchmarks (2025-10-31)
- TurboQuant discussion — GB10 baseline data on llama.cpp discussions #20969
- yunusshin/DGX_Spark_Qwen3.5-35B-A3B-Optimized — 64→113-115 tok/s (vLLM)
- Medium (Allen Kuo) — Speculative Decoding for Local LLMs + DFlash (2026-05-15)

---

## GB10 / DGX Spark Benchmarks

### rikkarth.com — Qwen3.6-35B-A3B-FP8 via vLLM

**Hardware:** GB10 SM121, 121 GiB unified LPDDR5x, 273 GB/s bandwidth
**vLLM:** 0.17.1, NVFP4 not yet mature on Spark
**Config:** `--max-model-len 262144 --gpu-memory-utilization 0.85 --enable-prefix-caching`

| Concurrency | Output tok/s | Peak tok/s | TTFT p50 | TPOT p50 |
|-------------|-------------|------------|----------|----------|
| c=1 | 21.0 | 33 | 363ms | 48ms |
| c=2 | 31.5 | 34 | 396ms | 62ms |
| c=4 | 51.5 | 60 | 510ms | 75ms |
| c=8 | 70.2 | 96 | 617ms | 98ms |
| c=16 | 115.8 | 160 | 861ms | 132ms |
| c=32 | 155.6 | 291 | 1121ms | 195ms |

**Key findings:**
- Single-user steady-state: **28-30 tok/s** (real-prompt sanity checks)
- Theoretical ceiling: 273 GB/s / 3 GB active = **91 tok/s** single-stream
- Real-world realizes ~32% of theoretical = normal for this class
- NVFP4 projected: **~55-60 tok/s** (2× theoretical with NVFP4)
- AWQ-Int4: +14% at c=1, +27% at c=4 vs FP8
- Memory-bandwidth bound, not KV-bound

### eugr/spark-vllm-docker — Qwen3.6-35B-A3B via vLLM+DFlash

**Hardware:** GB10 SM121
**Results:** ~50 tok/s sustained generation
**Config:** FP8 MoE, 262K context, ~43 GiB GPU memory at 38% utilization
**Note:** DFlash speculative decoding ready but requires vLLM build with DFlash support

### JetsonHacks llama-bench — GB10

**Build:** b6767 (5acd45546), SM 12.1, VMM: yes

| Model | Quant | tg32 | tg32 @ d4096 | tg32 @ d8192 | tg32 @ d16384 | tg32 @ d32768 |
|-------|-------|------|-------------|-------------|--------------|--------------|
| gpt-oss 20B MXFP4 MoE | — | 79.74 | 74.63 | 69.49 | 64.02 | 55.96 |
| gpt-oss 120B MXFP4 MoE | — | 52.87 | 51.02 | 48.46 | 44.78 | 38.76 |
| qwen3moe 30B.A3B | Q8_0 | 59.95 | 52.70 | 44.48 | 37.10 | 27.82 |
| qwen2 7B | Q8_0 | 29.40 | 28.31 | 27.53 | 26.03 | 22.08 |
| gemma3 4B | Q4_0 | 79.83 | 67.49 | 66.87 | 63.36 | 57.67 |
| glm4moe 106B.A12B | Q4_K | 22.59 | 20.10 | 18.78 | 16.47 | 13.19 |

**Key finding:** Context depth degrades MoE speed significantly. Qwen3 Coder 30B A3B drops from ~60 tok/s at d0 to ~28 tok/s at d32K.

### TurboQuant discussion (#20969) — GB10 baseline

**Hardware:** GB10 SM121
**Model:** Nemotron-3-Nano-30B-A3B Q4_K_XL
**llama.cpp build:** 8399

Generation throughput by context depth:
| Context | f16 KV | q8_0 KV | q4_0 KV |
|---------|--------|---------|---------|
| ~6K | 44.7 | 44.9 | 45.0 |
| ~24K | 44.6 | 39.7 | 39.3 |
| ~110K | 38.0 | 25.0 | 24.0 |

**Key finding:** KV cache quantization doesn't affect prompt throughput but degrades generation at long context due to per-token dequantization overhead. TurboQuant eliminates this by enabling direct computation on quantized values.

### yunusshin/DGX_Spark_Qwen3.5-35B-A3B-Optimized

**Result:** 64 → 113-115 tok/s (+77%)
**Engine:** vLLM (optimized)
**Model:** Qwen3.5-35B-A3B (not 3.6)
**Note:** Port of albond's v2 optimizations from Qwen3.5-122B down to 35B

### Reddit — "Solved the DGX Spark, 102 stable tok/s"

**Claim:** 102 tok/s baseline on Qwen3.5-35B-A3B, 125+ with MTP
**Engine:** llama.cpp or vLLM (unconfirmed which)
**Model:** Qwen3.5-35B-A3B (not 3.6)

---

## RTX 3090 Benchmarks (SM 86, 24GB, ~1000 GB/s GDDR6X)

### HackMD (thc1006) — Every llama.cpp spec-decode mode

**Hardware:** RTX 3090 24 GB, SM 8.6, driver 580.126, CUDA 12.0
**Model:** Qwen3.6-35B-A3B UD-Q4_K_XL
**Config:** `-ngl 999 -c 16384 -fa on -ctk q8_0 -ctv q8_0 -n 200`

| Config | Mean tok/s | Min | Max | Δ vs baseline | Draft acceptance |
|--------|-----------|-----|-----|--------------|-----------------|
| **baseline (no spec)** | **135.7** | 135.3 | — | — | — |
| DFlash --draft-max=8 | 77.0 | — | — | −44.6% | — |
| DFlash --draft-max=16 | 65.8 | — | — | −52.6% | — |
| DFlash --draft-max=4 | 74.9 | — | — | −46.1% | — |
| Oleg --draft-min 2 --draft-max 32 | 65.0 | 61.0 | 75.8 | −54% | 100% |
| srogmann --draft-min 48 --draft-max 64 | 85.6 | 81.3 | 88.0 | −39% | 100% |
| draft-q35-08b max{8,16,32} | 120-121 | 59-65 | — | — | 100% |
| ngram-cache | 119.1 | 65.3 | — | — | 100% |
| ngmod-n32 | 133.7 | 133.5 | — | — | 0% (never hits) |

**Key findings:**
- **No speculative decoding method beats baseline on RTX 3090**
- MTP draft model: 55-65 tok/s (−54 to −60%) despite 100% acceptance
- DFlash: 74.9-77 tok/s (−44 to −46%)
- ngram-mod: 129-131 tok/s (−3 to −6%)
- Mechanism: MoE expert-saturation threshold T_thres ≈ 94, K (1-32) ≪ T_thres
- Each drafted token pulls fresh expert slice through memory hierarchy
- 100% acceptance cannot rescue it — verify pass pays for full expert union

### carteakey.dev — RTX 4070 12GB

**Model:** unsloth/Qwen3.6-35B-A3B-MTP-GGUF (UD-Q4_K_XL)
**Config:** `--batch-size 1024 --ubatch-size 512 -ctk q8_0 -ctv q8_0`

| Task | Baseline | MTP n=2 | Accept | MTP n=3 | Accept |
|------|----------|---------|--------|---------|--------|
| Code (Python) | 51.3 | 66.4 | 97.4% | 69.1 | 95.3% |
| Code (C++) | 51.2 | 75.1 | 100.0% | 71.0 | 92.1% |
| Factual QA | 51.8 | 65.4 | 98.2% | 57.3 | 84.5% |
| Long Code Review | 51.0 | 62.3 | 98.2% | 55.5 | 81.3% |
| Stepwise Math | 51.1 | 67.5 | 99.2% | 66.3 | 92.1% |

**Key findings:**
- MTP n=2: 65-75 tok/s vs baseline ~51 tok/s (+28 to +47%)
- MTP n=3: 55-71 tok/s (varies, often worse than n=2)
- n=2 is sweet spot; n=3+ drops due to draft overhead
- Server-realistic: ~67 tok/s @ 128K context (MTP, accept rate ~98%)

### Allen Kuo (Medium) — RTX PRO 6000 Blackwell 96GB

**Hardware:** RTX PRO 6000 Blackwell (SM 12.1), 96 GB, AMD R9 9950X3D
**Key finding on MTP net win condition:**

```
MTP net win ⟺ (concurrency ≥ 4) ∧ (nspec ≥ 3) ∧ (accept ≥ 80%) ∧ (base decode not too fast)
```

- Single-stream MTP loses — verify cost is too high relative to single-stream decode
- NVFP4 baseline at ~57 tok/s makes MTP relatively less beneficial (verify cost is larger fraction of token budget)
- Qwen 3.6 has GDN layers (Gated DeltaNet) that don't parallelize well during speculative verify — verify cost grows close to linearly with n draft tokens

---

## Hardware Comparison

| Hardware | Compute Cap | Memory Bandwidth | Unified Mem | Notes |
|----------|------------|-----------------|-------------|-------|
| GB10 (DGX Spark) | SM 12.1 | 273 GB/s LPDDR5x | 128 GB | CPU-GPU unified |
| RTX 3090 | SM 8.6 | ~1000 GB/s GDDR6X | No | PCIe, 24 GB |
| RTX 4070 | SM 8.9 | ~240 GB/s GDDR6X | No | 12 GB |
| RTX PRO 6000 | SM 12.1 | TBD | 96 GB | Blackwell workstation |

**Key insight:** GB10 has ~4x less bandwidth than RTX 3090 (273 vs ~1000 GB/s). This is the dominant factor in throughput difference.

---

## Config Flags Reference

### llama.cpp flags relevant to Qwen3.6-35B-A3B

| Flag | Our Value | Effect |
|------|----------|--------|
| `--parallel` | 2 | Number of KV cache slots |
| `--flash-attn on` | yes | Flash attention (required for speed) |
| `--kv-unified` | yes | Unified KV cache (Qwen3.6 hybrid attention) |
| `--cache-prompt` | yes | Prompt caching |
| `--cache-reuse 4096` | yes | Min token overlap before reusing cached prefix |
| `--no-cache-idle-slots` | yes | Don't clear idle slot cache (slot pinning companion) |
| `--swa-full` | yes | Prevent SWA token pruning (hybrid model fix) |
| `--spec-type draft-mtp` | yes | Multi-token prediction speculative decoding |
| `--spec-draft-n-max 3` | yes | Max draft tokens per step |
| `--spec-draft-p-min 0.75` | yes | Min draft probability threshold |
| `--batch-size 4096` | yes | Prompt processing batch size |
| `--ubatch-size 2048` | yes | User batch size (decode) |
| `--ctx-checkpoints 32` | yes | Max checkpoints per slot |
| `--checkpoint-min-step 256` | yes | Min tokens between checkpoints |
| `--slot-prompt-similarity 0.5` | yes | Prompt similarity threshold for slot reuse |
| `--fit on` | yes | Fit context to target |
| `--fit-target 1024` | yes | Target tokens per fit step |
| `--fit-ctx 262144` | yes | Max context for fitting |

### KV cache quantization options

| Quant | Context ~6K | Context ~24K | Context ~110K | Notes |
|-------|------------|-------------|--------------|-------|
| f16 (baseline) | 44.7 | 44.6 | 38.0 | GB10 Nemotron-3-Nano |
| q8_0 | 44.9 | 39.7 | 25.0 | −11.9% at 24K, −36.8% at 110K |
| q4_0 | 45.0 | 39.3 | 24.0 | Same as q8_0 at long context |
| turbo3/turbo4 | TBD | TBD | TBD | TurboQuant eliminates dequant overhead |

---

## Open Questions for Future Testing

1. **Baseline (no MTP) on GB10** — current data only has MTP enabled
2. **KV cache quantization on our config** — q8_0 vs f16 impact
3. **Batch size tuning** — smaller ubatch-size for better throughput?
4. **Context depth sweep** — how does speed degrade at 32K, 64K, 128K, 262K?
5. **Different quant comparisons** — NVFP4 vs Q4_K_XL on GB10
6. **TurboQuant KV cache** — does it help on GB10?
7. **MTP n=2 vs n=3** — is n=2 better for our model?
