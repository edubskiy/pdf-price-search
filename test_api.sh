#!/bin/bash

# PDF Price Search API - Quick Test Script
# Run this to test all API endpoints

BASE_URL="http://localhost:8000"

echo "========================================="
echo "  PDF Price Search API - Test Suite"
echo "========================================="
echo

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Health Check
echo -e "${BLUE}[1/8] Health Check${NC}"
curl -s "${BASE_URL}/api/v1/health" | python3 -m json.tool
echo
echo

# Test 2: Search - FedEx 2Day
echo -e "${BLUE}[2/8] Search: FedEx 2Day, Zone 5, 3 lb${NC}"
curl -s -X POST "${BASE_URL}/api/v1/search" \
  -H 'Content-Type: application/json' \
  -d '{"query": "FedEx 2Day, Zone 5, 3 lb"}' | python3 -m json.tool
echo
echo

# Test 3: Search - Priority Overnight
echo -e "${BLUE}[3/8] Search: Priority Overnight, Zone 3, 5 lb${NC}"
curl -s -X POST "${BASE_URL}/api/v1/search" \
  -H 'Content-Type: application/json' \
  -d '{"query": "Priority Overnight, Zone 3, 5 lb"}' | python3 -m json.tool
echo
echo

# Test 4: Search - Express Saver
echo -e "${BLUE}[4/8] Search: Express Saver Z8 1 lb${NC}"
curl -s -X POST "${BASE_URL}/api/v1/search" \
  -H 'Content-Type: application/json' \
  -d '{"query": "Express Saver Z8 1 lb"}' | python3 -m json.tool
echo
echo

# Test 5: List All Services
echo -e "${BLUE}[5/8] List All Services${NC}"
curl -s "${BASE_URL}/api/v1/services" | python3 -m json.tool
echo
echo

# Test 6: Services Summary
echo -e "${BLUE}[6/8] Services Summary${NC}"
curl -s "${BASE_URL}/api/v1/services/summary" | python3 -m json.tool
echo
echo

# Test 7: Specific Service Details
echo -e "${BLUE}[7/8] Get FedEx 2Day Details${NC}"
curl -s "${BASE_URL}/api/v1/services/FedEx%202Day" | python3 -m json.tool
echo
echo

# Test 8: Cache Statistics
echo -e "${BLUE}[8/8] Cache Statistics${NC}"
curl -s "${BASE_URL}/api/v1/cache/stats" | python3 -m json.tool
echo
echo

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  All Tests Completed Successfully!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo
echo -e "API Documentation: ${YELLOW}http://localhost:8000/docs${NC}"
echo -e "Alternative Docs:  ${YELLOW}http://localhost:8000/redoc${NC}"
echo
