#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix the broken emoji in TRUSTED_SOURCES list"""

import os

# Read the file
with open('main_beautiful.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Replace the broken line with the correct one
old_line = '        "� Alt News (Fact-checker) - https://www.altnews.in",'
new_line = '        "📺 Alt News (Fact-checker) - https://www.altnews.in",'

# Try different possible corrupted versions
possible_corrupted = [
    '        "� Alt News (Fact-checker) - https://www.altnews.in",',
    '        "��� Alt News (Fact-checker) - https://www.altnews.in",',
]

for corrupted in possible_corrupted:
    if corrupted in content:
        content = content.replace(corrupted, new_line)
        print(f"Replaced: {corrupted[:30]}...")
        break

# Write back
with open('main_beautiful.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed Alt News emoji successfully!")
