find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete
# Remove database
rm db.sqlite3
# Reinstall django package
pip install --upgrade --force-reinstall Django
# Make migrations and migrate
python manage.py makemigrations
python manage.py migrate