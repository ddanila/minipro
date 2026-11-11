#!/usr/bin/env python3
import pathlib
import subprocess
import sys
import tempfile
with tempfile.TemporaryDirectory() as tmp:
    image = pathlib.Path(tmp) / 'target.bin'
    image.write_bytes(bytes([0xc3]) + bytes((i * 73) & 255 for i in range(1, 2048)))
    subprocess.run([sys.executable, str(pathlib.Path(__file__).with_name('test-rf2.py')),
                    sys.argv[1], str(image)], check=True)

    import os
    output = pathlib.Path(tmp) / '2732.bin'
    result = subprocess.run([str(pathlib.Path(sys.argv[1]).resolve()), '--serial',
                             '6MNNWV7B0LLRDYCAA5PF5744', 'read2732', str(output)],
                            env=os.environ | {'MOCK_2732': '1'}, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert output.read_bytes() == bytes((i ^ (i >> 8)) & 255 for i in range(4096))
    assert b'MOCK pulses=0 cleanup=OK' in result.stderr
    print('2732 all 12 address bits, pin 21 routing, zero pulses: PASS')
