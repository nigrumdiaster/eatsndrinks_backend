# **GRADUATION PROJECT**
<p align="center">
  <img src="https://miro.medium.com/v2/resize:fit:720/1*LYmZa7C58I9fk_SX3yCQkg.png" alt="Django + DRF Logo" height="100" />
  <img src="https://b2265571.smushcdn.com/2265571/wp-content/uploads/2022/07/ReactJS.png?lossy=2&strip=1&webp=1" alt="React Logo" height="100" />
</p>

***
<h2>Technologies Used:</h2>
<ul>
    <li>Python</li>
    <li>Django</li>
    <li>ReactJS</li>
</ul>

***
# How to run backend:
Prerequisites: - python 3.10
			   
### MySQL connect:
Setting your connect in this directory

    eatsndrinks/eatsndrinks/settings.py

The default passowrd for MySQL should be:
    
    123456

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
		



