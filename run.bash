#!/bin/bash
# run.bash v1.0 @ 2025-02-20 - nelbren@nelbren.com

if [ ! -r .venv/bin/activate ]; then
    echo "Please make my virtual environment! ( ./install.bash )"
    exit 1
fi

if [ ! -r config.yml -a \
     ! -r students.json ]; then
    echo "Please make config.yml! ( ./config.bash )"
    exit 2
fi

source .venv/bin/activate
flask run -p 8080 --host=0.0.0.0
