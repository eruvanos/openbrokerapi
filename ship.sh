set -e

git pull -r

./setup.py test

git push