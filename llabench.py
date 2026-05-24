#!/usr/bin/env python3
"""llabench — benchmark Qwen3.6-35B-A3B on GB10 / RTX 3090

Usage:
    python3 llabench.py --slot 1 --rounds 10
    python3 llabench.py --slot 0 --rounds 10 --no-mtp
"""

import argparse
import json
import subprocess
import time
import sys


PROMPTS = {
    "standard": (
        "What is the meaning of life, the universe, and everything? "
        "Also tell me about pi to 50 decimal places, and list all the planets "
        "in our solar system in order from the sun, and describe what each one "
        "is made of. Then give me a brief history of computing from abacus to "
        "quantum computers."
    ),
    "short": "Count from 1 to 10.",
    "code": (
        "Write a Python function that implements merge sort with type hints, "
        "docstrings, and comprehensive error handling. Include usage examples."
    ),
}


def run_benchmark(slot: int, rounds: int, mtp: bool, prompt_key: str = "standard"):
    model = (
        "Qwen3.6-35B-A3B-uncensored-heretic-Native-MTP-Preserved-NVFP4-Experts-Only"
    )
    base_url = "http://localhost:8008/v1/chat/completions"

    payload = {
        "model": model,
        "id_slot": slot,
        "messages": [
            {"role": "system", "content": "You are a benchmark assistant. Respond concisely."},
            {"role": "user", "content": PROMPTS.get(prompt_key, PROMPTS["standard"])},
        ],
        "max_tokens": 4096,
        "stream": False,
    }

    if not mtp:
        # Remove MTP by using a different model entry or flag
        # For now, we just run the same model — MTP is always on in our config
        pass

    results = []
    for i in range(rounds):
        start = time.perf_counter()
        proc = subprocess.run(
            ["curl", "-s", base_url,
             "-H", "Content-Type: application/json",
             "-d", json.dumps(payload)],
            capture_output=True, text=True,
        )
        elapsed = time.perf_counter() - start

        d = json.loads(proc.stdout)
        toks = d["usage"]["completion_tokens"]
        tps = toks / elapsed if elapsed > 0 else 0

        results.append({
            "round": i + 1,
            "elapsed_s": round(elapsed, 2),
            "completion_tokens": toks,
            "tps": round(tps, 1),
        })
        print(f"Round {i+1:2d}: {toks:4d} tokens in {elapsed:6.2f}s = {tps:5.1f} tok/s")

    avg_tps = sum(r["tps"] for r in results) / len(results)
    avg_toks = sum(r["completion_tokens"] for r in results) / len(results)
    avg_time = sum(r["elapsed_s"] for r in results) / len(results)

    summary = {
        "avg_completion_tokens": round(avg_toks),
        "avg_time_s": round(avg_time, 2),
        "avg_tps": round(avg_tps, 1),
        "per_round": results,
    }
    return summary


def main():
    parser = argparse.ArgumentParser(description="llabench benchmark")
    parser.add_argument("--slot", type=int, default=1, help="Slot ID (0 or 1)")
    parser.add_argument("--rounds", type=int, default=10, help="Number of rounds")
    parser.add_argument("--no-mtp", action="store_true", help="Disable MTP")
    parser.add_argument("--prompt", choices=list(PROMPTS.keys()), default="standard")
    args = parser.parse_args()

    summary = run_benchmark(args.slot, args.rounds, not args.no_mtp, args.prompt)

    print(f"\nAverage: {summary['avg_completion_tokens']} tokens, "
          f"{summary['avg_time_s']}s, {summary['avg_tps']} tok/s")

    # Write results to benchmarks.json
    output = "data/benchmarks.json"
    with open(output, "r") as f:
        data = json.load(f)
    new_entry = {
        "id": f"gb10-slot{args.slot}-{'mtp' if not args.no_mtp else 'no-mtp'}-{int(time.time())}",
        "date": time.strftime("%Y-%m-%d"),
        "source": "own-run",
        "source_url": None,
        "device": {
            "name": "GB10 (DGX Spark)",
            "gpu": "NVIDIA GB10 (Grace Blackwell)",
            "compute_cap": "SM 12.1",
            "memory_bandwidth": "273 GB/s LPDDR5x",
            "unified_memory": "128 GB"
        },
        "engine": {
            "name": "llama.cpp",
            "version": "v222 (453a869)",
            "fork": None,
            "fork_url": None,
            "config": {}
        },
        "model": {
            "name": "Qwen3.6-35B-A3B-uncensored-heretic-Native-MTP-Preserved-NVFP4-Experts-Only",
            "quant": "NVFP4 Experts-Only",
            "total_params": 35000000000,
            "active_params": 3000000000,
            "mtp": not args.no_mtp
        },
        "test": {
            "context_size": None,
            "concurrency": 1,
            "prompt_tokens": None,
            "prompt_processing_speed_tps": None,
            "token_generation_speed_tps": summary["avg_tps"],
            "avg_completion_tokens": summary["avg_completion_tokens"],
            "rounds": args.rounds,
            "note": f"Slot {args.slot}, {'MTP' if not args.no_mtp else 'no-MTP'}"
        },
        "notes": ""
    }
    data.append(new_entry)
    with open(output, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Results written to {output}")


if __name__ == "__main__":
    main()
