# How to run backend:
Prerequisites: python 3.10
### Create and activate virtual environment:
	python -m venv env
	# For Windows Command Prompt
	env\Scripts\activate
	
	# For Windows PowerShell
	.\env\Scripts\Activate.ps1
	
	# Install dependencies
	pip install -r requirements.txt

### Run Django migrations:
	cd eatsndrinks
 	python manage.py makemigrations
 	python manage.py migrate

### Start the Django development server:
	python manage.py runserver
In your web browser enter the address: http://localhost:8000 or http://127.0.0.1:8000/

### Test API:
	http://127.0.0.1:8000/swagger-ui
		
