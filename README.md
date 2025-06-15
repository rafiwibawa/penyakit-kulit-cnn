python3 -m venv venv

source venv/bin/activate  # Untuk Linux/macOS
# atau
venv\Scripts\activate     # Untuk Windows


pip install Flask Flask-Migrate Flask-SQLAlchemy PyMySQL python-dotenv flask-script

pip install joblib
pip install scikit-learn
pip install tensorflow
pip install Pillow 
pip install scikit-image

pip freeze > requirements.txt

./.venv/bin/python


export FLASK_APP=manage.py

flask db init
flask db migrate -m "initial migration"
flask db upgrade
