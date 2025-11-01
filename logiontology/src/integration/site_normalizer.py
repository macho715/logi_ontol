"""
HVDC Site/WH Code Normalizer v1.0
Normalizes site and warehouse codes to standard HVDC nomenclature
"""

from typing import Dict, Optional

# HVDC Site Codes (from ontology/HVDC.MD v3.0)
SITE_CODES: Dict[str, str] = {
    "AGI": "Al Ghallan Island",
    "AL GHALLAN": "Al Ghallan Island",
    "AL_GHALLAN": "Al Ghallan Island",
    "ALGHALLAN": "Al Ghallan Island",

    "DAS": "Das Island",
    "DAS ISLAND": "Das Island",
    "DAS_ISLAND": "Das Island",
    "DASISLAND": "Das Island",

    "MIR": "Mirfa Site",
    "MIRFA": "Mirfa Site",
    "MIRFA SITE": "Mirfa Site",
    "MIRFA_SITE": "Mirfa Site",

    "SHU": "Shuweihat Site",
    "SHUWEIHAT": "Shuweihat Site",
    "SHUWEIHAT SITE": "Shuweihat Site",
    "SHUWEIHAT_SITE": "Shuweihat Site",
}

# Reverse mapping: full name → code
SITE_CODE_REVERSE: Dict[str, str] = {
    "Al Ghallan Island": "AGI",
    "Das Island": "DAS",
    "Mirfa Site": "MIR",
    "Shuweihat Site": "SHU",
}

# Warehouse Codes
WH_CODES: Dict[str, str] = {
    "DSV": "DSV Indoor Warehouse",
    "DSV INDOOR": "DSV Indoor Warehouse",
    "DSV_INDOOR": "DSV Indoor Warehouse",
    "DSVINDOOR": "DSV Indoor Warehouse",

    "MOSB": "Mussafah Offshore Supply Base",
    "MUSSAFAH": "Mussafah Offshore Supply Base",
    "MUSSAFAH OFFSHORE": "Mussafah Offshore Supply Base",
    "MUSSAFAH_OFFSHORE": "Mussafah Offshore Supply Base",
}

# Reverse mapping: full name → code
WH_CODE_REVERSE: Dict[str, str] = {
    "DSV Indoor Warehouse": "DSV",
    "Mussafah Offshore Supply Base": "MOSB",
}

# Port Codes (from ontology/HVDC.MD v3.0)
PORT_CODES: Dict[str, str] = {
    "ZAYED": "Zayed Port",
    "ZAYED PORT": "Zayed Port",
    "ZAYED_PORT": "Zayed Port",
    "PORT ZAYED": "Zayed Port",
    "AEZYD": "Zayed Port",

    "KHALIFA": "Khalifa Port",
    "KHALIFA PORT": "Khalifa Port",
    "KHALIFA_PORT": "Khalifa Port",
    "PORT KHALIFA": "Khalifa Port",
    "AEKHL": "Khalifa Port",

    "JEBEL ALI": "Jebel Ali Port",
    "JEBEL_ALI": "Jebel Ali Port",
    "JEBEL ALI PORT": "Jebel Ali Port",
    "JEBEL_ALI_PORT": "Jebel Ali Port",
    "PORT JEBEL ALI": "Jebel Ali Port",
    "AEJEA": "Jebel Ali Port",
}

# Reverse mapping: full name → code
PORT_CODE_REVERSE: Dict[str, str] = {
    "Zayed Port": "ZAYED_PORT",
    "Khalifa Port": "KHALIFA_PORT",
    "Jebel Ali Port": "JEBEL_ALI_PORT",
}


class SiteNormalizer:
    """Normalize site, warehouse, and port codes"""

    def __init__(self):
        self.site_codes = SITE_CODES
        self.wh_codes = WH_CODES
        self.port_codes = PORT_CODES

    def normalize_site(self, code: str) -> Optional[str]:
        """
        Normalize site code to full name

        Args:
            code: Site code (e.g., "AGI", "DAS", "MIR", "SHU")

        Returns:
            Full site name or None if not found
        """
        if not code:
            return None

        normalized_key = code.upper().strip().replace("-", "_")
        return self.site_codes.get(normalized_key)

    def normalize_wh(self, code: str) -> Optional[str]:
        """
        Normalize warehouse code to full name

        Args:
            code: Warehouse code (e.g., "DSV", "MOSB")

        Returns:
            Full warehouse name or None if not found
        """
        if not code:
            return None

        normalized_key = code.upper().strip().replace("-", "_")
        return self.wh_codes.get(normalized_key)

    def normalize_port(self, code: str) -> Optional[str]:
        """
        Normalize port code to full name

        Args:
            code: Port code (e.g., "ZAYED", "KHALIFA", "JEBEL_ALI", "AEZYD")

        Returns:
            Full port name or None if not found
        """
        if not code:
            return None

        normalized_key = code.upper().strip().replace("-", "_")
        return self.port_codes.get(normalized_key)

    def get_site_code(self, full_name: str) -> Optional[str]:
        """
        Get site code from full name

        Args:
            full_name: Full site name (e.g., "Al Ghallan Island")

        Returns:
            Site code (e.g., "AGI") or None if not found
        """
        if not full_name:
            return None

        return SITE_CODE_REVERSE.get(full_name)

    def get_wh_code(self, full_name: str) -> Optional[str]:
        """
        Get warehouse code from full name

        Args:
            full_name: Full warehouse name (e.g., "DSV Indoor Warehouse")

        Returns:
            Warehouse code (e.g., "DSV") or None if not found
        """
        if not full_name:
            return None

        return WH_CODE_REVERSE.get(full_name)

    def get_port_code(self, full_name: str) -> Optional[str]:
        """
        Get port code from full name

        Args:
            full_name: Full port name (e.g., "Zayed Port")

        Returns:
            Port code (e.g., "ZAYED_PORT") or None if not found
        """
        if not full_name:
            return None

        return PORT_CODE_REVERSE.get(full_name)

    def is_offshore_site(self, code: str) -> bool:
        """
        Check if site is offshore (AGI, DAS)

        Args:
            code: Site code

        Returns:
            True if offshore site
        """
        normalized = self.get_site_code(self.normalize_site(code) or "")
        return normalized in ("AGI", "DAS")

    def is_onshore_site(self, code: str) -> bool:
        """
        Check if site is onshore (MIR, SHU)

        Args:
            code: Site code

        Returns:
            True if onshore site
        """
        normalized = self.get_site_code(self.normalize_site(code) or "")
        return normalized in ("MIR", "SHU")

    def get_all_sites(self) -> Dict[str, str]:
        """Get all site codes and names"""
        return {code: name for code, name in SITE_CODE_REVERSE.items()}

    def get_all_warehouses(self) -> Dict[str, str]:
        """Get all warehouse codes and names"""
        return {code: name for code, name in WH_CODE_REVERSE.items()}

    def get_all_ports(self) -> Dict[str, str]:
        """Get all port codes and names"""
        return {code: name for code, name in PORT_CODE_REVERSE.items()}

