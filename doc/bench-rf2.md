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

## Read-only 2732

`rf2-direct --serial EXPECTED_SERIAL read2732 OUTPUT` reuses the low-level read
controls for a standard DIP24 2732. It reads 4096 bytes with A11 on pin 21;
only pin 24 is connected to VCC, and OE/VPP pin 20 is driven low. No high-voltage
pin route or programming operation is enabled. The existing `write` command
remains RF2-only and requires an exact 2048-byte image. The test double checks
all 12 address bits, pin-21 routing and zero programming pulses.

## RF2 A9 drive and supply workaround

The `read` and `write` commands now enable the RF2 workaround by default:
release the normal A9 digital driver (DIP24 pin 22 / T48 ZIF38), route A9
through the VCC/GND matrix with break-before-make switching and OE gating,
and request VCC=5.18 V. Keep VCCIO at its default and read pin 21 on VCC.
The internal ADC must still report VCC within 4.75–5.25 V. Two A9-marked RF2
specimens passed independent partner writes with measured VCC around 5.09 V
reading and 5.14 V programming. This is not a measured silicon threshold.

Before writing, two full initial reads must agree. After the first pulse the
entire chip must match the tracked partial image, not just the current byte.
Every subsequent pulse also checks its A9 partner before proceeding. Failure
stops without retry and preserves the full readback after switching outputs
off; final verification and the caller's fresh reads are still required.
A blank image cannot establish address independence before a pulse.

`read2716 OUTPUT` preserves the old explicit 5 V digital-address read path for
standard single-supply 2716s; `read2732` is unchanged. Neither enables this RF2
workaround or permits programming. The standard MiniPro CLI is unchanged.

`make test-bench` exercises the actual writer with host-only injected A9 margin
and address-alias faults, a nonperiodic full image, partial writes, first-pulse
and later-partner corruption, unstable initial reads and fail-safe shutdown.
The model is explanatory, not an analog simulation. Full-image physical RF2
programming, retention and mainboard operation remain unqualified with this
new algorithm. Prior full-image burns used the earlier driver.

[Both specimens and detailed bench evidence](https://github.com/ddanila/rom-programmers/blob/main/docs/rf2-a9-investigation.md).
