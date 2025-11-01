"""Neo4j graph database store for HVDC ontology."""

from typing import Any, Dict, List, Optional
from pathlib import Path
import logging
import os

from neo4j import GraphDatabase, Driver
from rdflib import Graph, URIRef, Literal
import yaml

logger = logging.getLogger(__name__)


class Neo4jStore:
    """Neo4j graph database interface for RDF data."""

    def __init__(
        self,
        uri: str = None,
        user: str = None,
        password: str = None,
        database: str = "neo4j"
    ):
        """
        Initialize Neo4j connection.

        Args:
            uri: Neo4j URI (e.g., bolt://localhost:7687)
            user: Username
            password: Password
            database: Database name
        """
        # Load from config if not provided
        if uri is None or user is None or password is None:
            config = self._load_config()
            uri = uri or config['neo4j']['uri']
            user = user or config['neo4j']['user']
            password = password or os.getenv('NEO4J_PASSWORD') or config['neo4j']['password']
            database = database or config['neo4j'].get('database', 'neo4j')

        self.uri = uri
        self.user = user
        self.database = database
        self.driver: Optional[Driver] = None

        # Connect
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            logger.info(f"Connected to Neo4j at {uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    def _load_config(self) -> Dict:
        """Load Neo4j configuration from YAML."""
        config_path = Path(__file__).parent.parent.parent / "configs" / "neo4j_config.yaml"
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def close(self):
        """Close Neo4j driver connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")

    def execute_cypher(self, query: str, parameters: Dict = None) -> List[Dict]:
        """
        Execute Cypher query.

        Args:
            query: Cypher query string
            parameters: Query parameters

        Returns:
            List of result records as dictionaries
        """
        with self.driver.session(database=self.database) as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

    def load_rdf_graph(self, rdf_graph: Graph):
        """
        Load RDF triples into Neo4j as nodes and relationships.

        Args:
            rdf_graph: RDFLib Graph to load
        """
        logger.info(f"Loading {len(rdf_graph)} triples into Neo4j...")

        with self.driver.session(database=self.database) as session:
            # First pass: Create nodes
            for s, p, o in rdf_graph:
                if isinstance(o, URIRef):
                    # Object is a URI - create relationship
                    self._create_relationship(session, str(s), str(p), str(o))
                elif isinstance(o, Literal):
                    # Object is a literal - add as property
                    self._add_property(session, str(s), str(p), o)

        logger.info("RDF graph loaded into Neo4j successfully")

    def _create_relationship(self, session, subject: str, predicate: str, object: str):
        """Create a relationship between two nodes."""
        # Extract local names from URIs
        subj_label, subj_id = self._extract_node_info(subject)
        obj_label, obj_id = self._extract_node_info(object)
        rel_type = self._extract_relationship_type(predicate)

        query = """
        MERGE (a:{subj_label} {{uri: $subject, id: $subj_id}})
        MERGE (b:{obj_label} {{uri: $object, id: $obj_id}})
        MERGE (a)-[r:{rel_type}]->(b)
        """.format(subj_label=subj_label, obj_label=obj_label, rel_type=rel_type)

        session.run(query, subject=subject, subj_id=subj_id, object=object, obj_id=obj_id)

    def _add_property(self, session, subject: str, predicate: str, value: Literal):
        """Add a property to a node."""
        label, node_id = self._extract_node_info(subject)
        prop_name = self._extract_property_name(predicate)

        # Convert Literal value
        prop_value = str(value)
        if value.datatype:
            # Handle typed literals
            if 'integer' in str(value.datatype):
                prop_value = int(value)
            elif 'decimal' in str(value.datatype) or 'double' in str(value.datatype):
                prop_value = float(value)
            elif 'boolean' in str(value.datatype):
                prop_value = str(value).lower() in ('true', '1')

        query = """
        MERGE (n:{label} {{uri: $subject, id: $node_id}})
        SET n.{prop_name} = $value
        """.format(label=label, prop_name=prop_name)

        session.run(query, subject=subject, node_id=node_id, value=prop_value)

    def _extract_node_info(self, uri: str) -> tuple:
        """Extract label and ID from URI."""
        # Extract namespace and local name
        if '#' in uri:
            namespace, local = uri.rsplit('#', 1)
        elif '/' in uri:
            namespace, local = uri.rsplit('/', 1)
        else:
            return "Resource", uri

        # Determine label from local name
        if '-' in local:
            parts = local.split('-')
            label = parts[0].capitalize()
            node_id = '-'.join(parts[1:]) if len(parts) > 1 else local
        else:
            label = "Resource"
            node_id = local

        return label, node_id

    def _extract_relationship_type(self, predicate: str) -> str:
        """Extract relationship type from predicate URI."""
        if '#' in predicate:
            return predicate.rsplit('#', 1)[1].upper()
        elif '/' in predicate:
            return predicate.rsplit('/', 1)[1].upper()
        return "RELATED_TO"

    def _extract_property_name(self, predicate: str) -> str:
        """Extract property name from predicate URI."""
        if '#' in predicate:
            return predicate.rsplit('#', 1)[1]
        elif '/' in predicate:
            return predicate.rsplit('/', 1)[1]
        return predicate

    def create_indexes(self):
        """Create indexes from config."""
        config = self._load_config()
        indexes = config.get('indexes', [])

        with self.driver.session(database=self.database) as session:
            for index_query in indexes:
                try:
                    session.run(index_query)
                    logger.info(f"Created index: {index_query}")
                except Exception as e:
                    logger.warning(f"Index creation failed (may already exist): {e}")

    def create_constraints(self):
        """Create constraints from config."""
        config = self._load_config()
        constraints = config.get('constraints', [])

        with self.driver.session(database=self.database) as session:
            for constraint_query in constraints:
                try:
                    session.run(constraint_query)
                    logger.info(f"Created constraint: {constraint_query}")
                except Exception as e:
                    logger.warning(f"Constraint creation failed (may already exist): {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


