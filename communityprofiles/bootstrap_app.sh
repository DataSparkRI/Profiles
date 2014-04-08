#!/bin/bash

dropdb $1
createdb -T template_postgis $1

python manage.py syncdb

python manage.py migrate maps
python manage.py migrate
python manage.py loaddata profiles/fixtures/datasources.json
python manage.py loaddata profiles/fixtures/datadomains.json

python manage.py loaddata profiles/fixtures/sample_indicator.json
python manage.py loaddata profiles/fixtures/sample_indicators_parts.json

echo ""
echo "---------------------------------------------------------------------------------------------------------"
echo " Now run something like ./manage.py load_geographies census/tools/sample_data/pageo2010.sample.sf1 2010 "
