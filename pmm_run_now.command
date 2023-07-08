#! /bin/bash
cd /Users/silviovolley/Plex-Meta-Manager
python3 -m venv pmm-venv
source pmm-venv/bin/activate
pip install --upgrade pip
python -m pip install -r requirements.txt
sh pmm_main_run.sh

# pgrep -f pmm_run_now.command (to find the ID)
# kill ID (to stop the progress)