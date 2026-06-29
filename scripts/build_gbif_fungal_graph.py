"""
Build a small real-data fungal occurrence graph from GBIF.

This script:
1. Matches "Fungi" against the GBIF backbone taxonomy.
2. Fetches real fungal occurrence records with coordinates.
3. Saves cleaned occurrence records.
4. Builds a graph where:
   - taxon nodes represent fungal taxa
   - location nodes represent places
   - edges connect taxa to places where they were observed
5. Saves graph metrics for the learning lab UI.

Run from repo root:

    python scripts/build_gbif_fungal_graph.py
"""

from __future__ import annotations

import json
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import requests


GBIF_BASE_URL = "https://api.gbif.org/v1"

# Start small for a portfolio-friendly MVP.
# You can raise this later, but avoid hammering the API.
COUNTRY = "US"
LIMIT_PER_PAGE = 100
MAX_RECORDS = 300

# Project URL or email here eventually.
# GBIF recommends setting a useful User-Agent for apps/scripts.
USER_AGENT = "mycelium-learning-lab/0.1 https://github.com/sirhodess/mycelium-learning-lab"

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"


def gbif_get(path: str, params: dict[str, Any]) -> dict[str, Any]:
    """Make a GET request to GBIF and return JSON."""
    url = f"{GBIF_BASE_URL}{path}"
    response = requests.get(
        url,
        params=params,
        headers={"User-Agent": USER_AGENT},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def get_fungi_taxon_key() -> int:
    """
    Match the kingdom name "Fungi" to a GBIF usage key.

    GBIF species/match helps connect a name to the GBIF backbone taxonomy.
    """
    data = gbif_get(
        "/species/match",
        {
            "name": "Fungi",
            "rank": "KINGDOM",
            "verbose": "true",
        },
    )

    usage_key = data.get("usageKey")
    if not usage_key:
        raise RuntimeError(f"Could not find GBIF usageKey for Fungi: {data}")

    return int(usage_key)


def fetch_fungal_occurrences(taxon_key: int) -> list[dict[str, Any]]:
    """Fetch paged fungal occurrence records from GBIF."""
    records: list[dict[str, Any]] = []
    offset = 0

    while len(records) < MAX_RECORDS:
        remaining = MAX_RECORDS - len(records)
        page_limit = min(LIMIT_PER_PAGE, remaining)

        data = gbif_get(
            "/occurrence/search",
            {
                "taxonKey": taxon_key,
                "country": COUNTRY,
                "hasCoordinate": "true",
                "limit": page_limit,
                "offset": offset,
            },
        )

        results = data.get("results", [])
        if not results:
            break

        records.extend(results)
        offset += page_limit

        print(f"Fetched {len(records)} records...")

        # Be polite to the public API.
        time.sleep(0.25)

    return records


def clean_occurrence(record: dict[str, Any]) -> dict[str, Any]:
    """Keep only fields useful for the learning lab prototype."""
    return {
        "gbifID": record.get("gbifID"),
        "scientificName": record.get("scientificName"),
        "canonicalName": record.get("acceptedScientificName")
        or record.get("genericName")
        or record.get("scientificName"),
        "kingdom": record.get("kingdom"),
        "phylum": record.get("phylum"),
        "class": record.get("class"),
        "order": record.get("order"),
        "family": record.get("family"),
        "genus": record.get("genus"),
        "species": record.get("species"),
        "country": record.get("country"),
        "stateProvince": record.get("stateProvince"),
        "locality": record.get("locality"),
        "decimalLatitude": record.get("decimalLatitude"),
        "decimalLongitude": record.get("decimalLongitude"),
        "eventDate": record.get("eventDate"),
        "year": record.get("year"),
        "basisOfRecord": record.get("basisOfRecord"),
        "datasetName": record.get("datasetName"),
        "publisher": record.get("publisher"),
        "license": record.get("license"),
        "references": record.get("references"),
    }


def location_label(record: dict[str, Any]) -> str:
    """Create a readable place label from an occurrence record."""
    state = record.get("stateProvince")
    country = record.get("country")

    if state and country:
        return f"{state}, {country}"
    if country:
        return country
    return "Unknown location"


def taxon_label(record: dict[str, Any]) -> str:
    """Prefer species, then genus, then scientific name."""
    return (
        record.get("species")
        or record.get("genus")
        or record.get("canonicalName")
        or record.get("scientificName")
        or "Unknown taxon"
    )


def build_graph(records: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Build a bipartite graph:
    fungal taxon nodes <-> location nodes.

    This is real-data-derived: an edge means that taxon appeared
    in occurrence data for that location.
    """
    nodes: dict[str, dict[str, Any]] = {}
    edge_weights: Counter[tuple[str, str]] = Counter()

    taxon_occurrence_counts: Counter[str] = Counter()
    location_occurrence_counts: Counter[str] = Counter()

    for record in records:
        taxon = taxon_label(record)
        place = location_label(record)

        taxon_id = f"taxon::{taxon}"
        location_id = f"location::{place}"

        taxon_occurrence_counts[taxon_id] += 1
        location_occurrence_counts[location_id] += 1
        edge_weights[(taxon_id, location_id)] += 1

        nodes[taxon_id] = {
            "id": taxon_id,
            "label": taxon,
            "type": "taxon",
            "group": record.get("genus") or "Unknown genus",
        }

        nodes[location_id] = {
            "id": location_id,
            "label": place,
            "type": "location",
            "group": record.get("country") or "Unknown country",
        }

    for node_id, count in taxon_occurrence_counts.items():
        nodes[node_id]["occurrenceCount"] = count

    for node_id, count in location_occurrence_counts.items():
        nodes[node_id]["occurrenceCount"] = count

    edges = [
        {
            "id": f"{source}--{target}",
            "source": source,
            "target": target,
            "weight": weight,
            "relationship": "observed_in",
        }
        for (source, target), weight in edge_weights.items()
    ]

    return {
        "metadata": {
            "source": "GBIF Occurrence API",
            "countryFilter": COUNTRY,
            "recordCount": len(records),
            "description": (
                "A real-data-derived graph connecting fungal taxa to locations "
                "where GBIF occurrence records report them."
            ),
        },
        "nodes": list(nodes.values()),
        "edges": edges,
    }


def calculate_metrics(graph: dict[str, Any]) -> dict[str, Any]:
    """Calculate simple graph/network metrics for the learning lab."""
    nodes = graph["nodes"]
    edges = graph["edges"]

    degree: Counter[str] = Counter()
    weighted_degree: Counter[str] = Counter()

    adjacency: dict[str, set[str]] = defaultdict(set)

    for edge in edges:
        source = edge["source"]
        target = edge["target"]
        weight = edge.get("weight", 1)

        degree[source] += 1
        degree[target] += 1

        weighted_degree[source] += weight
        weighted_degree[target] += weight

        adjacency[source].add(target)
        adjacency[target].add(source)

    isolated_nodes = [node["id"] for node in nodes if degree[node["id"]] == 0]

    top_connected = [
        {
            "id": node_id,
            "degree": count,
            "weightedDegree": weighted_degree[node_id],
        }
        for node_id, count in degree.most_common(10)
    ]

    node_types = Counter(node["type"] for node in nodes)

    return {
        "totalNodes": len(nodes),
        "totalEdges": len(edges),
        "nodeTypes": dict(node_types),
        "isolatedNodeCount": len(isolated_nodes),
        "topConnectedNodes": top_connected,
        "averageDegree": round(sum(degree.values()) / len(nodes), 2) if nodes else 0,
        "interpretation": {
            "totalNodes": "How many taxa and location points exist in this graph.",
            "totalEdges": "How many observed-in relationships connect taxa to locations.",
            "topConnectedNodes": "Which taxa or locations have the most graph relationships.",
            "averageDegree": "The average number of relationships per node.",
            "isolatedNodeCount": "Nodes with no relationships. This should usually be 0 in this generated graph.",
        },
    }


def write_json(path: Path, data: Any) -> None:
    """Write pretty JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {path.relative_to(ROOT)}")


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("Finding GBIF taxon key for Fungi...")
    fungi_taxon_key = get_fungi_taxon_key()
    print(f"Fungi taxon key: {fungi_taxon_key}")

    print("Fetching fungal occurrence records from GBIF...")
    raw_records = fetch_fungal_occurrences(fungi_taxon_key)

    print("Cleaning records...")
    cleaned_records = [clean_occurrence(record) for record in raw_records]

    print("Building graph...")
    graph = build_graph(cleaned_records)

    print("Calculating metrics...")
    metrics = calculate_metrics(graph)

    write_json(RAW_DIR / "gbif_fungal_occurrences_raw.json", raw_records)
    write_json(PROCESSED_DIR / "fungal_occurrences.json", cleaned_records)
    write_json(PROCESSED_DIR / "fungal_network_graph.json", graph)
    write_json(PROCESSED_DIR / "fungal_network_metrics.json", metrics)

    print("\nDone.")
    print(f"Records: {len(cleaned_records)}")
    print(f"Nodes: {metrics['totalNodes']}")
    print(f"Edges: {metrics['totalEdges']}")


if __name__ == "__main__":
    main()