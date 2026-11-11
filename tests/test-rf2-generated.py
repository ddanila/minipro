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
