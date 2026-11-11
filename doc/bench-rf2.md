# Experimental T48 RF2 bench support

The `bench` branch preserves whaslbeck's contact-test additions on top of
David Griffith's MiniPro history. Our base was
cfe2171ca1b23399558b8d2a603a2ac3fa3faf5d. General fixes are separate commits.
The original whaslbeck checkout and acquisition evidence remain unchanged.

Build with `make minipro rf2-direct`; run hardware-free checks with
`make test-bench`. Standard libusb and zlib development packages are required.
For use without installation, build with `SHARE_INSTDIR="$PWD"`.

```
./rf2-direct --serial EXPECTED_SERIAL read result.bin
./rf2-direct --serial EXPECTED_SERIAL write image.bin result.bin 2048
```

RF2 support is explicit, fixed at the standard 2 KiB/24-pin pinout and nominal
50 ms positive CE pulses. It checks socket contact before powering the chip, then existing contents, skips correct bytes,
checks internal ADC voltages, verifies each byte, and stops at the first error.
It never erases. Exit 3 means a requested byte limit left work incomplete.
The serial is supplied by bench configuration; no device-specific serial is
compiled into the writer. A serial mismatch sends no pin-control commands.

Read VPP is explicitly tied to VCC. The native M2716 read/verify algorithm
returned false FF data on the tested RF2, including after a successful burn.
The exact firmware timing/routing cause remains unresolved. Do not substitute
the native path for RF2 verification or blank checking.

One RF2 specimen passed full W4 programming and two fresh reads. This is not
qualification of all RF2/2716 chips. Internal ADC and host pulse windows are
not calibrated chip-pin measurements or scope captures. Ordinary errors and
handled signals reset outputs; USB loss or forced process termination cannot
provide a hardware pulse watchdog. The direct raw-DAC VPP target is the bench
setting qualified in that session, with a 23.5–25.5 V ADC guard.

[Original evidence and provenance](https://github.com/ddanila/willem-v30/tree/ff2a7c3/programming/t48-rf2-w4-20261111).
[Common workflows](https://github.com/ddanila/rom-programmers).
