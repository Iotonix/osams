#!/bin/bash
rsync -avz --no-o --no-g --progress --exclude '.git' --exclude '.venv' --exclude '*.log' . osams:/srv/aims/SRC/osams/