# Check if database file exists and remove it if so
if [[ -e db.sqlite3 ]]; then
    rm db.sqlite3
fi
# Let django creating tables on database 
python manage.py migrate
# Create admin user (/admin) with specified username and email
python manage.py createsuperuser --email=admin@example.com --username=admin

# Creates default guns (main and side) and skin in the databse through django shell
echo -e "from api.models import Gun, Skin \n\
Skin.objects.create(name='Test skin 1', description='Nessuna descrizione', price=0) \n\
Gun.objects.create(name='Main gun 1', type=0, cooldown=1200, damage=10, description='Nessuna descrizione', price=0) \n\
Gun.objects.create(name='Side gun 1', type=1, cooldown=1800, damage=20, description='Nessuna descrizione', price=1000) \
" | python manage.py shell
echo "Default guns and skin created"