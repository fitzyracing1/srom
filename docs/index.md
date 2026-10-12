# SROM

SROM is a stored-program computer built on the AIC-1 inference core, written in plain Python. Memory holds the program, and a clock fetches, decodes and executes it. The boot ROM loads eight sensor features, runs MAC / ReLU / sigmoid, compares the result against 0.62, and writes the output port.

## Getting started

```
python3 srom.py      # writes srom_run.json
python3 ai_chip.py   # minimal AIC-1 core alone, writes ai_chip_says.json
```

The README records the last run as 26 cycles, port `1.0`, decision **ACT**.

## ISA (README)
`NOP LOAD STORE LDI ADD SUB MUL MAC RELU SIG CMP JMP JZ JGE IN OUT HALT`

## Files

| File | Role |
|---|---|
| `srom.py` | stored-program computer: memory, clock, fetch/decode/execute, boot ROM |
| `ai_chip.py` | AIC-1 core: 8 weights, bias 0.15, opcode stream RESET LOAD MAC RELU SIG THRESH WRITE HALT |
| `srom_run.json`, `ai_chip_says.json` | recorded outputs |
| `lithograph/PLATE.md`, `aic1-plate.svg` | lithograph plate of the AIC-1 core. `PLATE.md` names a stone photo and a print PDF that are not in the repo |

The repo has no tests, no CI and no LICENSE file.

Copyright (c) 2026 Joshua Almeida
