import os
import sys
from loguru import logger
from config_minimal import MinimalConfig, create_minimal_dependencies

# Import the logic from your script
# from scripts.seed_gwas_library import auto_seed_gwas_library
from scripts.seed_database import seed_gwas_library, seed_phenotypes

def main():
    logger.info("--- STARTING MINIMAL SEED TEST ---")
    
    config = MinimalConfig()
    deps = create_minimal_dependencies(config)
    
    # Run the seed logic
    # auto_seed_gwas_library(deps['gwas_library'], config.gwas_manifest_path)
    seed_gwas_library(deps['gwas_library'], config.gwas_manifest_path)
    seed_phenotypes(deps['phenotypes'], config.phenotypes_catalog_path)
    
    # Final check
    count = deps['gwas_library'].get_entry_count()
    logger.success(f"Final Count in Database: {count}")

if __name__ == "__main__":
    main()