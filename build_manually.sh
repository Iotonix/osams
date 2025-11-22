#!/bin/bash
# This script builds the Docker image for the Nexus Spell Checker application. 
# This is for testing that the build works before we attempt the github actions
docker build --no-cache -t hugo:0.1 -t registry.ait.co.th/iotonix/hugo:0.1 -t registry.ait.co.th/iotonix/hugo:latest -f Dockerfile .
