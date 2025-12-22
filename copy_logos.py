#!/usr/bin/env python
"""Helper script to copy logo files to static/images folder"""
import shutil
import os

# Get the directory of this script
base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)

# Logo files
logos = [
    'logo_square_no_name_1024x1024.png',
    'logo_square_with_name_1024x1024.png',
    'logo_vertical_512x256.png'
]

# Destination folder
dest_folder = os.path.join(base_dir, 'static', 'images')
os.makedirs(dest_folder, exist_ok=True)

# Copy files
for logo in logos:
    src = os.path.join(parent_dir, logo)
    if os.path.exists(src):
        shutil.copy(src, dest_folder)
        print(f"Copied: {logo}")
    else:
        print(f"Not found: {src}")

print("\nDone! Logos copied to static/images/")

