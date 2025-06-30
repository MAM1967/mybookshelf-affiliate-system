#!/bin/bash
# Cron job script for scheduled LinkedIn posting
cd "$(dirname "$0")/.."
python3 scripts/scheduled_linkedin_poster_simple.py
