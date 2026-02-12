#!/usr/bin/env python3
import os
import sys
from loguru import logger
from pathlib import Path

# Fix pathing for local imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from .gwas_manifest_parser import GWASManifestParser

def auto_seed_gwas_library(gwas_handler, manifest_path):
    """
    Logic for seeding. This is called by main.py on startup.
    It is idempotent: it only runs if the collection is empty.
    """
    if not manifest_path or not os.path.exists(manifest_path):
        logger.warning(f"GWAS Manifest not found at {manifest_path}. Skipping auto-seed.")
        return

    # 1. Check if we actually need to seed
    count = gwas_handler.get_entry_count()
    if count > 0:
        logger.info(f"GWAS library already contains {count} entries. Skipping seed.")
        return

    # 2. Perform seeding
    logger.info(f"GWAS library is empty. Auto-seeding from {manifest_path}...")
    try:
        parser = GWASManifestParser(manifest_path)
        entries = parser.parse()
        valid_entries, _, _ = parser.validate_entries(entries)
        
        if valid_entries:
            result = gwas_handler.bulk_create_gwas_entries(valid_entries)
            logger.success(f"Successfully auto-seeded {result['inserted_count']} GWAS entries.")
    except Exception as e:
        logger.error(f"Auto-seeding failed: {e}")

# This part is ONLY for terminal use (Manual Maintenance)
if __name__ == "__main__":
    import argparse
    from dotenv import load_dotenv
    from db import GWASLibraryHandler
    
    load_dotenv()
    parser = argparse.ArgumentParser(description="Manual Seed Script")
    parser.add_argument("--manifest", default="../data/Manifest_201807.csv")
    args = parser.parse_args()

    uri, db = os.getenv('MONGODB_URI'), os.getenv('DB_NAME')
    if uri and db:
        handler = GWASLibraryHandler(uri, db)
        # We call the same function here!
        auto_seed_gwas_library(handler, args.manifest)