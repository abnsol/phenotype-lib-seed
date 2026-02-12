import argparse
import os
from flask import Flask
from flask_restful import Api
from loguru import logger
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from werkzeug.formparser import FormDataParser

from config import Config, create_dependencies
from logging_config import setup_logging
from socketio_instance import socketio
from status_tracker import StatusTracker
from gwas_manifest_parser import GWASManifestParser # Added import
from api import (
    CredibleSetsAPI, EnrichAPI, HypothesisAPI, BulkHypothesisDeleteAPI,
    ChatAPI, init_socket_handlers, ProjectsAPI, AnalysisPipelineAPI,
    GWASFilesAPI, GWASFileDownloadAPI, UserFilesAPI,
)
from scripts.seed_gwas_library import auto_seed_gwas_library

def parse_flask_arguments():
    parser = argparse.ArgumentParser(description="Flask Application Server")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--embedding-model", type=str, default="w601sxs/b1ade-embed-kd")
    parser.add_argument("--swipl-host", type=str, default="localhost")
    parser.add_argument("--swipl-port", type=int, default=4242)
    parser.add_argument("--ensembl-hgnc-map", type=str, required=True)
    parser.add_argument("--hgnc-ensembl-map", type=str, required=True)
    parser.add_argument("--go-map", type=str, required=True)
    # Added argument
    parser.add_argument("--gwas-manifest", type=str, default="./data/Manifest_201807.csv")
    
    return parser.parse_args()

def setup_api(config):
    load_dotenv()
    app = Flask(__name__)

    # (JWT and App Configs remain the same...)
    app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
    app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024
    
    jwt = JWTManager(app)
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    api = Api(app)
    socketio.init_app(app)

    deps = create_dependencies(config)
    
    status_tracker = StatusTracker()
    status_tracker.initialize(deps['tasks'])

    # Setup API endpoints
    api.add_resource(EnrichAPI, "/enrich", resource_class_kwargs={"enrichr": deps['enrichr'], "llm": deps['llm'], "prolog_query": deps['prolog_query'], "enrichment": deps['enrichment'], "hypotheses": deps['hypotheses'], "projects": deps['projects'], "gene_expression": deps['gene_expression']})
    api.add_resource(HypothesisAPI, "/hypothesis", resource_class_kwargs={"enrichr": deps['enrichr'], "prolog_query": deps['prolog_query'], "llm": deps['llm'], "hypotheses": deps['hypotheses'], "enrichment": deps['enrichment']})
    api.add_resource(ChatAPI, "/chat", resource_class_kwargs={"llm": deps['llm'], "hypotheses": deps['hypotheses']})
    api.add_resource(BulkHypothesisDeleteAPI, "/hypothesis/delete", resource_class_kwargs={"hypotheses": deps['hypotheses']})
    api.add_resource(ProjectsAPI, "/projects", resource_class_kwargs={"projects": deps['projects'], "files": deps['files'], "analysis": deps['analysis'], "hypotheses": deps['hypotheses'], "enrichment": deps['enrichment'], "gene_expression": deps['gene_expression']})
    api.add_resource(AnalysisPipelineAPI, "/analysis-pipeline", resource_class_kwargs={"projects": deps['projects'], "files": deps['files'], "analysis": deps['analysis'], "gene_expression": deps['gene_expression'], "config": config, "storage": deps['storage'], "gwas_library": deps['gwas_library']})
    api.add_resource(CredibleSetsAPI, "/credible-sets", resource_class_kwargs={"analysis": deps['analysis']})
    api.add_resource(GWASFilesAPI, "/gwas-files", resource_class_kwargs={"config": config, "gwas_library": deps['gwas_library'], "storage": deps['storage']})
    api.add_resource(GWASFileDownloadAPI, "/gwas-files/download/<string:file_id>", resource_class_kwargs={"config": config, "gwas_library": deps['gwas_library'], "storage": deps['storage']})
    api.add_resource(UserFilesAPI, "/user-files", resource_class_kwargs={"files": deps['files'], "storage": deps['storage']})

    init_socket_handlers(deps['hypotheses'])
    
    # Updated: Return deps so main() can use them
    return app, socketio, deps

def main():
    args = parse_flask_arguments()
    config = Config.from_args(args)
    setup_logging(log_level='INFO')  

    if not all([config.ensembl_hgnc_map, config.hgnc_ensembl_map, config.go_map]):
        raise ValueError("Missing required mapping data files.")
    
    app, socketio, deps = setup_api(config)

    # Trigger idempotent seeding
    auto_seed_gwas_library(deps['gwas_library'], config.gwas_manifest_path)

    logger.info(f"Starting Flask application on {config.host}:{config.port}")
    socketio.run(app, host=config.host, port=config.port, debug=False, use_reloader=False, allow_unsafe_werkzeug=True)

if __name__ == "__main__":
    main()