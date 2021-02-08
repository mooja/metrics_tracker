#!/usr/bin/bash

# run manage.py commands locally without docker

export DATABASE_URL=sqlite:////home/mooja/projects/metrics_tracker/db.sqlite3
export DEBUG=true
export ALLOWED_HOSTS=0.0.0.0,localhost
export SECRET_KEY="abracadabjra"
export CACHE_URL=locmemcache://

./manage.py "$@"
