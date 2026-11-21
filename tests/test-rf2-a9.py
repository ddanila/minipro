#!/usr/bin/env python3
"""Execute production RF2 code with a host-only fault model, never USB."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

EXE = str(Path(sys.argv.pop(1)).resolve())
SERIAL = '6MNNWV7B0LLRDYCAA5PF5744'


class RF2A9Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def run_chip(self, initial, target=None, flags=None, command='read', limit=2048, serial=SERIAL):
        before, result, physical = [self.root/n for n in ('before.bin', 'result.bin', 'physical.bin')]
        before.write_bytes(initial)
        result.unlink(missing_ok=True)
        physical.unlink(missing_ok=True)
        env = {k: v for k, v in os.environ.items() if not k.startswith('MOCK_')}
        env.update(MOCK_IMAGE=str(before), MOCK_PHYSICAL_OUT=str(physical), MOCK_A9_MARGIN='1')
        env.update(flags or {})
        args = [EXE, '--serial', serial]
        if target is None:
            args += [command, str(result)]
        else:
            image = self.root/'target.bin'
            image.write_bytes(target)
            args += ['write', str(image), str(result), str(limit)]
        proc = subprocess.run(args, env=env, capture_output=True, text=True, timeout=10)
        self.assertIn('cleanup=OK', proc.stderr)
        return proc, result.read_bytes() if result.exists() else None, physical.read_bytes() if physical.exists() else None

    def test_default_rf2_read_distinguishes_all_address_bits(self):
        initial = bytes(((a * 73) ^ (a >> 3) ^ (a >> 8) * 37) & 255 for a in range(2048))
        p, data, physical = self.run_chip(initial)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(data, initial)
        self.assertEqual(physical, initial)
        self.assertIn('MOCK pulses=0', p.stderr)

    def test_generic_2716_read_keeps_legacy_drive_and_supply(self):
        initial = bytes(((a * 73) ^ (a >> 8)) & 255 for a in range(2048))
        p, data, _ = self.run_chip(initial, command='read2716', flags={'MOCK_EXPECT_LEGACY': '1'})
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(data, bytes(initial[a & ~0x200] for a in range(2048)))
        self.assertIn('MOCK pulses=0', p.stderr)

    def test_full_nonperiodic_image_under_a9_margin_fault(self):
        initial = bytes([255])*2048
        target = bytes(((a * 73) ^ (a >> 3) ^ (a >> 8) * 37) & 255 for a in range(2048))
        p, data, physical = self.run_chip(initial, target)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(data, target)
        self.assertEqual(physical, target)
        self.assertIn(f'MOCK pulses={sum(v != 255 for v in target)} ', p.stderr)

    def test_partial_existing_data_and_single_byte_limit(self):
        initial = bytearray([255]*2048)
        initial[0x70] = 0xfe
        target = bytearray(initial)
        target[0x270] = 0xfd
        target[0x670] = 0xf7
        p, data, physical = self.run_chip(initial, target, limit=1)
        self.assertEqual(p.returncode, 3, p.stderr)
        expected = bytearray(initial)
        expected[0x270] = 0xfd
        self.assertEqual(data, expected)
        self.assertEqual(physical, expected)
        self.assertIn('MOCK pulses=1 ', p.stderr)

    def test_alias_on_any_address_bit_stops_after_first_pulse(self):
        for bit in (0, 8, 9, 10):
            with self.subTest(bit=bit):
                initial = bytes([255])*2048
                target = bytearray(initial)
                target[1 << bit] = 0xfe
                target[(1 << bit)+2] = 0xfc
                p, data, _ = self.run_chip(initial, target, flags={'MOCK_ALIAS_BIT': str(bit)})
                self.assertEqual(p.returncode, 1, p.stderr)
                self.assertIn('first-pulse full-chip verification mismatch', p.stderr)
                self.assertIn('MOCK pulses=1 ', p.stderr)
                self.assertIsNotNone(data)
                self.assertNotEqual(data, target)

    def test_partner_corruption_on_later_pulse_stops_before_third(self):
        initial = bytes([255])*2048
        target = bytearray(initial)
        target[0x10], target[0x110], target[0x120] = 0xfe, 0xfd, 0xfb
        p, data, _ = self.run_chip(initial, target, flags={'MOCK_LATE_A9': '1'})
        self.assertEqual(p.returncode, 1, p.stderr)
        self.assertIn('A9 partner changed', p.stderr)
        self.assertIn('MOCK pulses=2 ', p.stderr)
        self.assertEqual(data[0x120], 255)
        self.assertEqual(data[0x310], 0xfd)

    def test_unstable_initial_read_never_pulses(self):
        initial = bytes([255])*2048
        target = bytearray(initial)
        target[0x270] = 0xfd
        p, _, physical = self.run_chip(initial, target, flags={'MOCK_UNSTABLE': '1'})
        self.assertEqual(p.returncode, 1, p.stderr)
        self.assertIn('initial reads unstable', p.stderr)
        self.assertIn('MOCK pulses=0 ', p.stderr)
        self.assertEqual(physical, initial)

    def test_failures_do_not_retry_and_shutdown(self):
        initial = bytes([255])*2048
        target = bytearray(initial)
        target[0x270] = 0xfd
        for flag, pulses in [('MOCK_CONTACT_FAIL', 0), ('MOCK_OVERVOLT', 0), ('MOCK_VERIFY_FAIL', 1)]:
            with self.subTest(flag=flag):
                p, _, physical = self.run_chip(initial, target, flags={flag: '1'})
                self.assertEqual(p.returncode, 1, p.stderr)
                self.assertIn(f'MOCK pulses={pulses} ', p.stderr)
                self.assertEqual(physical, initial)


if __name__ == '__main__':
    unittest.main()
