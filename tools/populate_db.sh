# Check if database file exists and remove it if so
if [[ -e db.sqlite3 ]]; then
    rm db.sqlite3
fi
# Let django creating tables on database 
python manage.py migrate
# Create admin user (/admin) with specified username and email
echo -e "\nCreating admin profile:"
python manage.py createsuperuser --email=admin@example.com --username=admin

echo -e "\n"
# Creates default guns (main and side) and skin in the databse through django shell
python manage.py populatedb --username bot-1 --userpass test_password --json