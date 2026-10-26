# SROM

Stored-program computer built on the AIC-1 inference core.

Memory holds the program. A clock fetches, decodes, and executes. The boot ROM loads eight sensor features, runs MAC / ReLU / sigmoid, compares against 0.62, and writes the output port.

Last run: 26 cycles, port `1.0`, decision **ACT**.

```
python3 srom.py
```

Writes `srom_run.json`.

ISA: NOP LOAD STORE LDI ADD SUB MUL MAC RELU SIG CMP JMP JZ JGE IN OUT HALT.

## Documentation

- In-repo docs: [docs/](docs/index.md)
- Wiki: [https://github.com/fitzyracing1/srom/wiki](https://github.com/fitzyracing1/srom/wiki)

## Plans

This project is free, and its license stays as is. Support it through [GitHub Sponsors](https://github.com/sponsors/fitzyracing1):

- **Free**: use the code, community support.
- **Pro ($49/month)**: priority issues and support.
- **Team ($199/month)**: priority support for your team plus early access.
