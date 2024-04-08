#!/usr/bin/env sh

echo "=== create config ==="
python /home/${USER}/install/create_config.py

echo "=== database setup ==="
/home/${USER}/install/database_setup.sh
