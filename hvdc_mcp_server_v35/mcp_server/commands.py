import click
from .sparql_engine import SPARQLEngine

engine = SPARQLEngine()

@click.group()
def cli():
    pass

@cli.command()
def flow_code_distribution_v35():
    """Distribution with Flow 0-5"""
    dist = engine.get_flow_code_distribution_v35()
    for item in dist:
        print(f"Flow {item['flowCode']}: {item['count']} cases - {item['description']}")

@cli.command()
def agi_das_compliance():
    """Validate domain rules"""
    comp = engine.get_agi_das_compliance()
    print(f"Total AGI/DAS: {comp['total_agi_das']}")
    print(f"Compliant: {comp['compliant_count']}")
    print(f"Rate: {comp['compliance_rate']:.2f}%")

@cli.command()
def override_cases():
    """Get all overridden cases"""
    overrides = engine.get_override_cases()
    for ov in overrides:
        print(f"Case {ov['caseId']}: Original {ov['flowCodeOrig']} -> {ov['flowCode']} (Reason: {ov['reason']}, Loc: {ov['finalLoc']})")

@cli.command()
@click.argument('case_id')
def case_lookup(case_id):
    """Updated case lookup"""
    case = engine.get_case(case_id)
    if case:
        click.echo(case)
    else:
        click.echo("Case not found.")

@cli.command()
def flow_5_analysis():
    """Analyze mixed/incomplete cases"""
    analysis = engine.get_flow_5_analysis()
    for item in analysis:
        print(f"Case {item['caseId']}: Vendor={item.get('vendor', 'N/A')}, HVDC Code={item.get('hvdcCode', 'N/A')}")

@cli.command()
def pre_arrival_status():
    """Get Flow 0 cases"""
    cases = engine.get_pre_arrival_status()
    for case in cases:
        print(f"Case {case['caseId']}: Vendor={case.get('vendor', 'N/A')}, HVDC Code={case.get('hvdcCode', 'N/A')}")

if __name__ == '__main__':
    cli()

