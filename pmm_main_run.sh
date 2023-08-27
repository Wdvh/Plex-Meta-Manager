#! /bin/bash
python3 favorites.py
sleep 15s
python3 returning.py
sleep 15s
python3 plex_meta_manager.py --config config/config_mass_updates.yml --run 
sleep 15s
python3 plex_meta_manager.py --config config/config_metadata_update.yml --run 
sleep 15s
python3 plex_meta_manager.py --config config/config.yml --run
