#!/bin/bash

# 1. Apne Cabelwala project folder me jao (Agar NAS pe path alag hai to isko change kar lena)
cd /volume1/docker/cabelwala/

# --- FIX START ---
# Git permission error fix karne ke liye ye line jodi hai
git config --global --add safe.directory /volume1/docker/cabelwala
# --- FIX END ---

# 2. GitHub se naya code khicho
echo "Pulling latest code from GitHub..."
git pull origin main

# 3. Docker container ko naye code ke sath rebuild karo
echo "Rebuilding Cabelwala Docker container..."
sudo docker-compose up -d --build

echo "Update Complete! 🚀"