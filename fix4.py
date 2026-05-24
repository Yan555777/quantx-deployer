"""Apply Fix 4: add gc.collect() after each trade yield in options_backtest.py"""
import ast
from pathlib import Path

src_path = Path("api/options_backtest.py")
src = src_path.read_text(encoding="utf-8")

# Find the exact line from the file
old = '        yield {"type": "trade", "trade": trade}\n'
new = '        yield {"type": "trade", "trade": trade}\n        gc.collect()  # free parquet DataFrames from this trade\n'

if old in src:
    src = src.replace(old, new, 1)  # only first occurrence
    print("✅ Fix 4: Added gc.collect() after each trade")
else:
    # Try to find what's actually there
    lines = src.splitlines()
    for i, line in enumerate(lines, 1):
        if 'yield' in line and 'trade' in line:
            print(f"  Line {i}: {repr(line)}")
    print("❌ Fix 4: Could not apply — see lines above")
    exit(1)

try:
    ast.parse(src)
    print("✅ Syntax OK")
except SyntaxError as e:
    print(f"❌ Syntax ERROR: {e}")
    exit(1)

src_path.write_text(src, encoding="utf-8")
print("✅ Saved")
