#!/bin/bash
#
# Get Code Back from Vultr Server
# Usage: ./get_back_from_vultr.sh [--dry-run]
#
# Syncs remote project from Vultr server to local directory
# Project name is automatically detected from current directory
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REMOTE_USER="ralf"
REMOTE_HOST="osams"
REMOTE_BASE_PATH="/srv/aims/SRC"

# Auto-detect project name from current directory
PROJECT_NAME=$(basename "$(pwd)")

# Parse arguments
DRY_RUN=""
if [[ "$1" == "--dry-run" ]]; then
    DRY_RUN="--dry-run"
    echo -e "${YELLOW}🔍 DRY RUN MODE - No files will be transferred${NC}"
    echo ""
fi

# Build remote path
REMOTE_PATH="${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_BASE_PATH}/${PROJECT_NAME}/"

# Display configuration
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}📥 Getting code back from Vultr${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "  Project:     ${GREEN}${PROJECT_NAME}${NC}"
echo -e "  Remote:      ${YELLOW}${REMOTE_PATH}${NC}"
echo -e "  Local:       ${BLUE}$(pwd)${NC}"
[[ -n "$DRY_RUN" ]] && echo -e "  Mode:        ${YELLOW}DRY RUN${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Exclusions (don't overwrite local critical files)
EXCLUDES=(
    '.git'
    '.venv'
    'venv'
    '__pycache__'
    '*.pyc'
    '*.pyo'
    '*.log'
    '.env'
    '.env.local'
    '.env.docker'
    '.DS_Store'
    'node_modules'
    '*.swp'
    '*.swo'
    '*~'
    '.pytest_cache'
    '.coverage'
    'htmlcov'
    'postgres_data'
    'mongo_data'
    'staticfiles'
    'media'
    'release2vultr.sh'
    'get_back_from_vultr.sh'
)

# Build exclude flags
EXCLUDE_FLAGS=()
for item in "${EXCLUDES[@]}"; do
    EXCLUDE_FLAGS+=(--exclude "$item")
done

# Confirm before proceeding (skip in dry-run)
if [[ -z "$DRY_RUN" ]]; then
    echo -e "${YELLOW}⚠️  This will overwrite local files with remote versions.${NC}"
    echo -e "${YELLOW}⚠️  Your local .env and .venv will be preserved.${NC}"
    read -p "Continue? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}❌ Cancelled${NC}"
        exit 1
    fi
    echo ""
fi

# Run rsync
echo -e "${GREEN}🚀 Starting sync...${NC}"
echo ""

rsync -avz \
    --no-o --no-g \
    --progress \
    --human-readable \
    --itemize-changes \
    "${EXCLUDE_FLAGS[@]}" \
    $DRY_RUN \
    "$REMOTE_PATH" .

EXIT_CODE=$?

echo ""
if [[ $EXIT_CODE -eq 0 ]]; then
    if [[ -n "$DRY_RUN" ]]; then
        echo -e "${GREEN}✅ Dry run completed successfully${NC}"
        echo -e "${YELLOW}💡 Run without --dry-run to actually transfer files${NC}"
    else
        echo -e "${GREEN}✅ Sync completed successfully${NC}"
        echo -e "${BLUE}📦 Remote changes from '${PROJECT_NAME}' are now local${NC}"
        echo ""
        echo -e "${YELLOW}Next steps:${NC}"
        echo -e "  1. Review changes:  ${BLUE}git status${NC}"
        echo -e "  2. Test locally:    ${BLUE}docker-compose up -d${NC}"
        echo -e "  3. Commit changes:  ${BLUE}git add . && git commit${NC}"
    fi
else
    echo -e "${RED}❌ Sync failed with exit code ${EXIT_CODE}${NC}"
    exit $EXIT_CODE
fi
