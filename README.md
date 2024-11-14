# Cloud Computing Practical 2
### Eoin Noonan Treacy - 23221675 

## Exercise One
### Run and test
```bash
cd exercise_one/
docker compose up --build # optional [-d] for detached if you want to do this all in one shell

# environment to run tests // these will fail without database runing from above
python -m venv .venv
# activate environment
source .venv/bin/activate
# install requirements
pip install -r requirements
# run tests
pytest
# stop everything
docker compose down
```