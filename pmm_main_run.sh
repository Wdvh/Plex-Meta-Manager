#! /bin/bash
python3 /Users/silviovolley/backupyml/returning.py
python3 plex_meta_manager.py --config config/config_mass_updates.yml --run 
python3 plex_meta_manager.py --config config/config_metadata_update.yml --run 
python3 plex_meta_manager.py --config config/config.yml --run
