import os
from db.gwas_library_handler import GWASLibraryHandler

class MinimalConfig:
    def __init__(self):
        # Point to your Docker Mongo
        self.mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.db_name = os.getenv("DB_NAME", "hypothesis_db")
        self.gwas_manifest_path = "./data/Manifest_201807.csv"

def create_minimal_dependencies(config):
    return {
        'gwas_library': GWASLibraryHandler(config.mongodb_uri, config.db_name)
    } 