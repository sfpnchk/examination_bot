venv/bin/activate:
	python3.10 -m venv venv

setup:
	. venv/bin/activate;
	pip install -r requirements.txt
run:
	. venv/bin/activate;
	python3.10 entry.py --run

revision:
	. venv/bin/activate;
	python entry.py --revision

migrate:
	. venv/bin/activate;
	python entry.py --migrate
