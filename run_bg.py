"""Run Streamlit with BACKGROUND_IMAGE_URL set from the local SVG sample.
This script sets the env var and launches Streamlit using the same Python interpreter.
It does not modify git or commit files.
"""
import base64
import os
import subprocess
from pathlib import Path

svg_path = Path(__file__).resolve().parents[0] / 'assets' / 'transparent_bg_sample.svg'
if not svg_path.exists():
    print('SVG not found:', svg_path)
    raise SystemExit(1)

with svg_path.open('rb') as f:
    b = f.read()

b64 = base64.b64encode(b).decode('ascii')
bg = 'data:image/svg+xml;base64,' + b64

# Build env with BACKGROUND_IMAGE_URL
env = os.environ.copy()
env['BACKGROUND_IMAGE_URL'] = bg

python_exe = os.environ.get('PYTHON_EXECUTABLE') or 'python'

cmd = [python_exe, '-m', 'streamlit', 'run', str(Path(__file__).resolve().parents[0] / 'main_beautiful.py'), '--server.port', '8501']
print('Launching Streamlit with command:', ' '.join(cmd))
print('Background data-URI length:', len(bg))

# Launch Streamlit (will run until stopped)
subprocess.run(cmd, env=env)
