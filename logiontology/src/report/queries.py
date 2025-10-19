from __future__ import annotations

def q_inventory_by_sku() -> str:
    return """
    PREFIX ex: <http://example.org/lo/>
    SELECT ?sku (SUM(?qty) AS ?total)
    WHERE {
      ?s ex:sku_id ?sku ;
         ex:quantity ?qty .
    } GROUP BY ?sku
    """.strip()

def q_lead_time_distribution() -> str:
    return """
    PREFIX ex: <http://example.org/lo/>
    SELECT ?shipment_id ?depart ?arrive (xsd:dateTime(?arrive) - xsd:dateTime(?depart) AS ?lead_time)
    WHERE { ?s ex:shipment_id ?shipment_id ; ex:depart_at ?depart ; ex:arrive_at ?arrive . }
    """.strip()
