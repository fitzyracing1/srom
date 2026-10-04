#!/usr/bin/env python3
"""SROM: a stored-program computer built around the AIC-1 inference core.

Memory holds the program. The clock fetches, decodes, and executes.
Nothing runs unless it was loaded into ROM first.
"""
from __future__ import annotations

import json
from pathlib import Path

MEM_WORDS = 64
ROM_WEIGHTS = [0.42, -0.18, 0.91, 0.07, -0.33, 0.55, 0.12, -0.64]
BIAS = 0.15

OP = {
    "NOP": 0x00,
    "LOAD": 0x01,
    "STORE": 0x02,
    "LDI": 0x03,
    "ADD": 0x04,
    "SUB": 0x05,
    "MUL": 0x06,
    "MAC": 0x07,
    "RELU": 0x08,
    "SIG": 0x09,
    "CMP": 0x0A,
    "JMP": 0x0B,
    "JZ": 0x0C,
    "JGE": 0x0D,
    "IN": 0x0E,
    "OUT": 0x0F,
    "HALT": 0x10,
}

MNEM = {v: k for k, v in OP.items()}


def sigmoid(x: float) -> float:
    if x >= 0:
        z = pow(2.718281828, -x)
        return 1.0 / (1.0 + z)
    z = pow(2.718281828, x)
    return z / (1.0 + z)


class SROM:
    def __init__(self) -> None:
        self.mem = [0.0] * MEM_WORDS
        self.pc = 0
        self.ir = 0
        self.acc = 0.0
        self.halted = False
        self.z = False
        self.ge = False
        self.cycle = 0
        self.sensor = 0.0
        self.ports = []
        self.trace = []
        self.prog = {}
        self.prog_len = 0

    def load_program(self, words):
        for i, (op, operand, imm) in enumerate(words):
            self.mem[i] = float(operand)
            self.prog[i] = (op, operand, imm)
        self.prog_len = len(words)

    def reset(self) -> None:
        self.pc = 0
        self.ir = 0
        self.acc = 0.0
        self.halted = False
        self.z = False
        self.ge = False
        self.cycle = 0
        self.ports.clear()
        self.trace.clear()

    def step(self) -> None:
        if self.halted:
            return
        if self.pc >= self.prog_len:
            self.halted = True
            return
        op, operand, imm = self.prog[self.pc]
        self.ir = op
        self.cycle += 1
        name = MNEM.get(op, f"ILL_{op}")
        before = self.pc
        self._exec(op, operand, imm)
        self.trace.append({"cycle": self.cycle, "pc": before, "op": name, "operand": operand, "acc": round(self.acc, 6), "z": self.z, "ge": self.ge})

    def _exec(self, op, operand, imm) -> None:
        nxt = self.pc + 1
        if op == OP["NOP"]:
            pass
        elif op == OP["LOAD"]:
            self.acc = self.mem[operand]
        elif op == OP["STORE"]:
            self.mem[operand] = self.acc
        elif op == OP["LDI"]:
            self.acc = float(imm if imm is not None else operand)
        elif op == OP["ADD"]:
            self.acc += self.mem[operand]
        elif op == OP["SUB"]:
            self.acc -= self.mem[operand]
        elif op == OP["MUL"]:
            self.acc *= self.mem[operand]
        elif op == OP["MAC"]:
            acc = BIAS
            for i in range(8):
                acc += self.mem[operand + i] * ROM_WEIGHTS[i]
            self.acc = acc
        elif op == OP["RELU"]:
            self.acc = self.acc if self.acc > 0 else 0.0
        elif op == OP["SIG"]:
            self.acc = sigmoid(self.acc)
        elif op == OP["CMP"]:
            other = self.mem[operand]
            self.z = abs(self.acc - other) < 1e-9
            self.ge = self.acc >= other
        elif op == OP["JMP"]:
            nxt = operand
        elif op == OP["JZ"]:
            if self.z:
                nxt = operand
        elif op == OP["JGE"]:
            if self.ge:
                nxt = operand
        elif op == OP["IN"]:
            self.acc = self.sensor
        elif op == OP["OUT"]:
            self.ports.append(self.acc)
        elif op == OP["HALT"]:
            self.halted = True
        else:
            raise RuntimeError(f"illegal opcode {op} at pc {self.pc}")
        self.pc = nxt
        if op == OP["HALT"]:
            self.halted = True

    def run(self, limit: int = 200) -> None:
        while not self.halted and self.cycle < limit:
            self.step()


def assemble(lines):
    out = []
    for raw in lines:
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        mnem = parts[0].upper()
        if mnem not in OP:
            raise SystemExit(f"unknown mnemonic {mnem}")
        operand = int(parts[1]) if len(parts) > 1 else 0
        imm = float(parts[2]) if len(parts) > 2 else None
        out.append((OP[mnem], operand, imm))
    return out


PROGRAM = [
    "LDI 0 0.8",
    "STORE 32",
    "LDI 0 0.2",
    "STORE 33",
    "LDI 0 1.1",
    "STORE 34",
    "LDI 0 -0.4",
    "STORE 35",
    "LDI 0 0.5",
    "STORE 36",
    "LDI 0 0.3",
    "STORE 37",
    "LDI 0 0.9",
    "STORE 38",
    "LDI 0 -0.1",
    "STORE 39",
    "LDI 0 0.62",
    "STORE 40",
    "MAC 32",
    "RELU 0",
    "SIG 0",
    "CMP 40",
    "JGE 26",
    "LDI 0 0",
    "OUT 0",
    "JMP 28",
    "LDI 0 1",
    "OUT 0",
    "HALT 0",
]


def main() -> None:
    cpu = SROM()
    words = assemble(PROGRAM)
    cpu.load_program(words)
    cpu.reset()
    cpu.run()
    action = "ACT" if cpu.ports and cpu.ports[-1] == 1.0 else "HOLD"
    report = {
        "machine": "SROM",
        "kind": "stored-program computer",
        "mem_words": MEM_WORDS,
        "rom_weights": ROM_WEIGHTS,
        "bias": BIAS,
        "cycles": cpu.cycle,
        "halted": cpu.halted,
        "acc": round(cpu.acc, 6),
        "ports": cpu.ports,
        "decision": action,
        "trace": cpu.trace,
    }
    out = Path(__file__).with_name("srom_run.json")
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ("machine", "cycles", "acc", "ports", "decision", "halted")}, indent=2))


if __name__ == "__main__":
    main()
