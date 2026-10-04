#!/usr/bin/env python3
"""Minimal AI chip: emits its own instruction stream, host obeys every opcode."""
import json
import math
from pathlib import Path

ROM = {
    "w": [0.42, -0.18, 0.91, 0.07, -0.33, 0.55, 0.12, -0.64],
    "b": 0.15,
}
SRAM = [0.0] * 16
LOG = []


def issue(op, **kw):
    insn = {"op": op, **kw}
    LOG.append(insn)
    return exec_op(insn)


def exec_op(insn):
    op = insn["op"]
    if op == "RESET":
        for i in range(len(SRAM)):
            SRAM[i] = 0.0
        return "sram cleared"
    if op == "LOAD_SENSOR":
        vec = insn["vec"]
        for i, v in enumerate(vec):
            SRAM[i] = float(v)
        return f"loaded {len(vec)} features"
    if op == "MAC":
        n = insn["n"]
        acc = ROM["b"]
        for i in range(n):
            acc += SRAM[i] * ROM["w"][i]
        SRAM[8] = acc
        return f"mac={acc:.6f}"
    if op == "RELU":
        SRAM[9] = max(0.0, SRAM[8])
        return f"relu={SRAM[9]:.6f}"
    if op == "SIGMOID":
        x = SRAM[9]
        SRAM[10] = 1.0 / (1.0 + math.exp(-x))
        return f"sigmoid={SRAM[10]:.6f}"
    if op == "THRESHOLD":
        fire = SRAM[10] >= insn["t"]
        SRAM[11] = 1.0 if fire else 0.0
        return f"fire={int(fire)} @ t={insn['t']}"
    if op == "WRITE_OUT":
        return {
            "score": round(SRAM[10], 6),
            "gate": int(SRAM[11]),
            "action": "ACT" if SRAM[11] else "HOLD",
        }
    if op == "HALT":
        return "halt"
    raise RuntimeError(f"illegal opcode {op}")


def run():
    program = [
        ("RESET", {}),
        ("LOAD_SENSOR", {"vec": [0.8, 0.2, 1.1, -0.4, 0.5, 0.3, 0.9, -0.1]}),
        ("MAC", {"n": 8}),
        ("RELU", {}),
        ("SIGMOID", {}),
        ("THRESHOLD", {"t": 0.62}),
        ("WRITE_OUT", {}),
        ("HALT", {}),
    ]
    trace = []
    result = None
    for op, kw in program:
        out = issue(op, **kw)
        trace.append({"issued": op, "result": out})
        if op == "WRITE_OUT":
            result = out
    return {
        "chip": "AIC-1 inference core",
        "directive": "obey every opcode the chip issues",
        "rom_weights": ROM,
        "instruction_trace": trace,
        "chip_decision": result,
        "sram_final": [round(x, 6) for x in SRAM],
    }


if __name__ == "__main__":
    report = run()
    outp = Path(__file__).with_name("ai_chip_says.json")
    outp.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
