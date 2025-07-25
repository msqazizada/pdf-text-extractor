import json


def enrich_country_info(text: str, data: dict) -> dict | None:
    """
    Tries to fill all 3 fields (Land, Länderkürzel, EUTPD) from any one of them.

    Returns a dict like:
    {
        "Land": "Germany",
        "Länderkürzel": "DE",
        "EUTPD": "EUTPD"
    }
    or None if not matched.
    """
    text_clean = text.strip().lower()

    # Try match by code (e.g., DE)
    if text_clean in data:
        info = data[text_clean]
        return {
            "Länderkürzel": text_clean.upper(),
            "Land": info["country"],
            "EUTPD": "EUTPD" if info["eutpd"] else "-"
        }

    # Try match by country name (e.g., Germany)
    for code, info in data.items():
        if info["country"].lower() == text_clean:
            return {
                "Länderkürzel": code,
                "Land": info["country"],
                "EUTPD": "EUTPD" if info["eutpd"] else "-"
            }

    return None


def load_country_data(json_path="country_data.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


COUNTRY_DATA = load_country_data()


def get_country_info_by_code(code: str, data: dict) -> dict | None:
    info = data.get(code)
    if info:
        return {
            "Länderkürzel": code,
            "Land": info["country"],
            "EUTPD": "EUTPD" if info["eutpd"] else "-"
        }
    return None


def get_country_info_by_name(name: str, data: dict) -> dict | None:
    for code, info in data.items():
        if info["country"].lower() == name.lower():
            return {
                "Länderkürzel": code,
                "Land": info["country"],
                "EUTPD": "EUTPD" if info["eutpd"] else "-"
            }
    return None
