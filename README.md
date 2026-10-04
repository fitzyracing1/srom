# SROM

Stored-program computer built on the AIC-1 inference core.

Memory holds the program. A clock fetches, decodes, and executes. The boot ROM loads eight sensor features, runs MAC / ReLU / sigmoid, compares against 0.62, and writes the output port.

Last run: 26 cycles, port `1.0`, decision **ACT**.

```
python3 srom.py
```

Writes `srom_run.json`.

ISA: NOP LOAD STORE LDI ADD SUB MUL MAC RELU SIG CMP JMP JZ JGE IN OUT HALT.
