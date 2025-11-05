"""
Quick test of query parser
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.domain.services.query_parser import QueryParser

parser = QueryParser()

test_queries = [
    "2lb to zone 5",
    "zone 5 2lb",
    "FedEx 2Day, zone 5, 2 lb",
]

print("Testing Query Parser:\n")
for query in test_queries:
    print(f"Query: '{query}'")
    try:
        result = parser.parse(query)
        print(f"  ✓ SUCCESS: service={result.service_type}, zone={result.zone.value}, weight={result.weight.value}")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
    print()
