if [[ ! -r frontend ]]; then
    # Clone repository
    git clone git@github.com:SmL-Boi/Gioele-V3.git frontend
else
    echo "FrontEnd found, updating..."
    # Update local repository
    git pull origin master
fi

# Copy static files fron local repository to django app
echo "Copying static files..."
cp frontend/game/*.js game/static/game/
cp frontend/game/*.css game/static/game/
cp frontend/game/*.png game/static/game/images/

# Attempts to replace static imports with django static import function
echo "Transforming index.html (fixing static imports)..."
echo "{% load static %}" | cat - frontend/game/index.html > temp.html
cat temp.html | grep -E -o "\"[a-z]+\.(js|css)\"" | tr -d '"' | while read line; do
    echo -e $(cat temp.html | sed 's/'"$line"'/{% static \x27game\/'"$line"'\x27 %}/') > temp.html
done
cp temp.html game/templates/game/index.html

# Attempts to correct static imports path of images in javascript (mainly skins)
echo "Transforming main.js (fixing static imports)..."
cp frontend/game/main.js temp.js
cat temp.js | grep -E -o "([a-z]|[A-Z]|[0-9])+\.png" | while read line; do
    echo -e $(cat temp.js | sed 's/'"$line"'/static\/game\/images\/'"$line"'/') > temp.js
done
cp temp.js game/static/game/main.js

echo "Cleaning up"
rm temp.html temp.js

echo "Upstream updated."