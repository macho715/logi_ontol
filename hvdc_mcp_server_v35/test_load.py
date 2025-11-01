#!/usr/bin/env python3
import sys
sys.path.insert(0, '..')

from mcp_server.sparql_engine import SPARQLEngine

print("Loading TTL file...")
engine = SPARQLEngine()
print(f"TTL loaded: {len(engine.graph)} triples")

print("\nTesting Flow Code distribution query...")
dist = engine.get_flow_code_distribution_v35()
print(f"Flow codes found: {len(dist)}")
for d in dist:
    print(f"  Flow {d['flowCode']}: {d['count']} - {d['description']}")

print("\nTesting AGI/DAS compliance...")
comp = engine.get_agi_das_compliance()
print(f"  Total AGI/DAS: {comp['total_agi_das']}")
print(f"  Compliant: {comp['compliant_count']}")
print(f"  Rate: {comp['compliance_rate']:.2f}%")

print("\nTesting override cases...")
overrides = engine.get_override_cases()
print(f"  Override cases found: {len(overrides)}")
if overrides:
    print(f"  Sample: Case {overrides[0]['caseId']}")

print("\n✓ All queries executed successfully!")

