"""
Command routing for MCP TTL Server
Maps command names to SPARQL engine methods
"""
from typing import Dict, Any
from .sparql_engine import SPARQLEngine


def execute_command(engine: SPARQLEngine, command: str, params: Dict[str, Any]) -> Any:
    """
    Execute MCP command and return results

    Args:
        engine: SPARQLEngine instance
        command: Command name
        params: Command parameters

    Returns:
        Query results

    Raises:
        ValueError: If command is unknown or params are invalid
    """
    command_map = {
        "case_lookup": _execute_case_lookup,
        "monthly_warehouse": _execute_monthly_warehouse,
        "vendor_summary": _execute_vendor_summary,
        "flow_distribution": _execute_flow_distribution,
        "search_by_location": _execute_search_by_location,
        "search_by_date_range": _execute_search_by_date_range,
        "sparql_query": _execute_sparql_query,
        "statistics": _execute_statistics,
    }

    if command not in command_map:
        raise ValueError(f"Unknown command: {command}. Available: {list(command_map.keys())}")

    return command_map[command](engine, params)


def _execute_case_lookup(engine: SPARQLEngine, params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute case_lookup command"""
    case_id = params.get("case_id")
    if not case_id:
        raise ValueError("case_id parameter is required")

    return engine.get_case_by_id(case_id)


def _execute_monthly_warehouse(engine: SPARQLEngine, params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute monthly_warehouse command"""
    year_month = params.get("year_month")
    if not year_month:
        raise ValueError("year_month parameter is required (format: YYYY-MM)")

    results = engine.get_monthly_warehouse(year_month)
    return {
        "year_month": year_month,
        "warehouses": results,
        "total_events": sum(int(r.get("event_count", 0)) for r in results)
    }


def _execute_vendor_summary(engine: SPARQLEngine, params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute vendor_summary command"""
    vendor = params.get("vendor")  # Optional filter

    results = engine.get_vendor_summary(vendor)
    return {
        "vendor_filter": vendor,
        "vendors": results,
        "total_vendors": len(results)
    }


def _execute_flow_distribution(engine: SPARQLEngine, params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute flow_distribution command"""
    results = engine.get_flow_distribution()
    return {
        "flows": results,
        "total_cases": sum(int(r.get("count", 0)) for r in results)
    }


def _execute_search_by_location(engine: SPARQLEngine, params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute search_by_location command"""
    location = params.get("location")
    if not location:
        raise ValueError("location parameter is required")

    results = engine.search_by_location(location)
    return {
        "location": location,
        "events": results,
        "total_events": len(results)
    }


def _execute_search_by_date_range(engine: SPARQLEngine, params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute search_by_date_range command"""
    start_date = params.get("start_date")
    end_date = params.get("end_date")

    if not start_date or not end_date:
        raise ValueError("start_date and end_date parameters are required (format: YYYY-MM-DD)")

    results = engine.search_by_date_range(start_date, end_date)
    return {
        "start_date": start_date,
        "end_date": end_date,
        "events": results,
        "total_events": len(results)
    }


def _execute_sparql_query(engine: SPARQLEngine, params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute custom SPARQL query"""
    sparql_query = params.get("query")
    if not sparql_query:
        raise ValueError("query parameter is required")

    results = engine.execute_query(sparql_query)
    return {
        "query": sparql_query,
        "results": results,
        "count": len(results)
    }


def _execute_statistics(engine: SPARQLEngine, params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute statistics command"""
    return engine.get_statistics()


# Command descriptions for /commands endpoint
COMMAND_DESCRIPTIONS = {
    "case_lookup": {
        "description": "Lookup case by ID",
        "params": {
            "case_id": "Case ID (e.g., 'Case_00045' or '00045')"
        },
        "example": {
            "command": "case_lookup",
            "params": {"case_id": "Case_00045"}
        }
    },
    "monthly_warehouse": {
        "description": "Monthly warehouse inbound/outbound summary",
        "params": {
            "year_month": "Year-month in YYYY-MM format (e.g., '2024-03')"
        },
        "example": {
            "command": "monthly_warehouse",
            "params": {"year_month": "2024-03"}
        }
    },
    "vendor_summary": {
        "description": "Vendor summary with case counts",
        "params": {
            "vendor": "(Optional) Vendor name filter"
        },
        "example": {
            "command": "vendor_summary",
            "params": {}
        }
    },
    "flow_distribution": {
        "description": "Distribution of cases by FLOW code",
        "params": {},
        "example": {
            "command": "flow_distribution",
            "params": {}
        }
    },
    "search_by_location": {
        "description": "Search events by location",
        "params": {
            "location": "Location name (e.g., 'MOSB', 'DAS', 'DSV Indoor')"
        },
        "example": {
            "command": "search_by_location",
            "params": {"location": "MOSB"}
        }
    },
    "search_by_date_range": {
        "description": "Search events by date range",
        "params": {
            "start_date": "Start date (YYYY-MM-DD)",
            "end_date": "End date (YYYY-MM-DD)"
        },
        "example": {
            "command": "search_by_date_range",
            "params": {"start_date": "2024-01-01", "end_date": "2024-12-31"}
        }
    },
    "sparql_query": {
        "description": "Execute custom SPARQL SELECT query",
        "params": {
            "query": "SPARQL SELECT query string"
        },
        "example": {
            "command": "sparql_query",
            "params": {"query": "PREFIX hvdc: <http://samsung.com/project-logistics#> SELECT ?s WHERE { ?s a hvdc:Case } LIMIT 10"}
        }
    },
    "statistics": {
        "description": "Get overall TTL statistics",
        "params": {},
        "example": {
            "command": "statistics",
            "params": {}
        }
    }
}


