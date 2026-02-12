docker-compose -f docker-compose-test.yml up -d
source .venv/bin/activate 
pip install pymongo loguru python-dotenv
python main_minimal.py

# test it (conut = 0)
docker exec -it mongo-test-seed mongosh --port 27017 --eval "db.getSiblingDB('hypothesis_db').gwas_library.countDocuments()"
docker exec -it mongo-test-seed mongosh hypothesis_db --eval "db.phenotypes.findOne()"

# empty it 
docker exec -it mongo-test-seed mongosh hypothesis_db --eval "db.gwas_library.drop()"
docker exec -it mongo-test-seed mongosh hypothesis_db --eval "db.phenotypes.drop()"

# test it (count = 11930)
# number of entries the same as what is in csv 
docker exec -it mongo-test-seed mongosh --port 27017 --eval "db.getSiblingDB('hypothesis_db').gwas_library.countDocuments()"