import os
from db.gwas_library_handler import GWASLibraryHandler
from db.phenotype_handler import PhenotypeHandler

class MinimalConfig:
    def __init__(self):
        # Point to your Docker Mongo
        self.mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.db_name = os.getenv("DB_NAME", "hypothesis_db")
        self.gwas_manifest_path = "./data/Manifest_201807.csv"
        self.phenotypes_catalog_path = "./data/gwas_catalog_phenotypes.json"

def create_minimal_dependencies(config):
    return {
        'gwas_library': GWASLibraryHandler(config.mongodb_uri, config.db_name),
        'phenotypes': PhenotypeHandler(config.mongodb_uri, config.db_name)
    } 