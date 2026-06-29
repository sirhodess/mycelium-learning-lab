# Setup Guide

This guide explains how to set up and run the current **Mycelium Learning Lab** prototype locally.

The current prototype uses public fungal occurrence data to generate a network graph, then displays that graph in a browser-based visualizer.

---

## Requirements

Before running the project, make sure you have:

- Python 3
- Git
- A modern web browser
- Internet access for fetching public fungal data

---

## 1. Clone the Repository

```bash
git clone https://github.com/sirhodess/mycelium-learning-lab.git
cd mycelium-learning-lab
```

If you already have the repository on your machine, move into the project folder:

```bash
cd /Users/sierrarhodes/github_projects/mycelium-learning-lab
```

---

## 2. Create a Virtual Environment

Create a Python virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

After activation, your terminal should show `(.venv)` at the beginning of the prompt.

Example:

```bash
(.venv) sierrarhodes@Mac mycelium-learning-lab %
```

---

## 3. Install Dependencies

Install the project dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

This installs the Python packages needed to fetch and process the fungal occurrence data.

---

## 4. Build the Fungal Graph Data

Run the GBIF fungal graph builder script:

```bash
python scripts/build_gbif_fungal_graph.py
```

This script fetches public fungal occurrence records and creates processed graph files.

Generated files should appear in:

```text
data/processed/
```

Expected files include:

```text
fungal_occurrences.json
fungal_network_graph.json
fungal_network_metrics.json
```

These files are used by the browser visualizer.

---

## 5. Start a Local Server

From the repository root, start a local development server:

```bash
python3 -m http.server 5173
```

Keep this terminal window open while using the visualizer.

---

## 6. Open the Visualizer

Open this URL in your browser:

```text
http://localhost:5173/experiments/fungal-network-viewer/
```

Do not open the HTML file by double-clicking it. The visualizer needs the local server so it can load the generated JSON files.

---

## Full Setup Flow

For a fresh setup, run:

```bash
cd /Users/sierrarhodes/github_projects/mycelium-learning-lab

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

python scripts/build_gbif_fungal_graph.py

python3 -m http.server 5173
```

Then open:

```text
http://localhost:5173/experiments/fungal-network-viewer/
```

---

## Updating the Data

To fetch fresh fungal occurrence data and rebuild the graph, run:

```bash
source .venv/bin/activate
python scripts/build_gbif_fungal_graph.py
```

Then refresh the browser page.

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'requests'`

This usually means the dependency was not installed in the Python environment currently running the script.

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Then reinstall dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the script again:

```bash
python scripts/build_gbif_fungal_graph.py
```

---

### The terminal does not show `(.venv)`

The virtual environment is not active.

Run:

```bash
source .venv/bin/activate
```

---

### `Could not load data`

This usually means the visualizer cannot find the generated JSON files.

Run the data script first:

```bash
python scripts/build_gbif_fungal_graph.py
```

Then restart the local server:

```bash
python3 -m http.server 5173
```

Open the visualizer again:

```text
http://localhost:5173/experiments/fungal-network-viewer/
```

---

### The visualizer opens, but the graph does not appear

Make sure you are running the local server from the repository root, not from inside the `experiments` folder.

Correct:

```bash
cd /Users/sierrarhodes/github_projects/mycelium-learning-lab
python3 -m http.server 5173
```

Then open:

```text
http://localhost:5173/experiments/fungal-network-viewer/
```

---

## Data and Modeling Notes

This project separates real data from educational modeling.

Real-data-derived parts include:

- fungal occurrence records
- taxon names
- location information
- taxon-location relationships
- graph nodes and edges
- network metrics

Educational modeling parts include:

- signal pulse animations
- future growth simulations
- future resource-sharing demonstrations
- future stress-test interactions

The goal is not to claim exact biological measurement of underground mycelial behavior. The goal is to use real fungal data and interactive simulations to make ecological networks and computing concepts easier to explore.

---

## Current Prototype

The current prototype is located at:

```text
experiments/fungal-network-viewer/
```

It displays a real-data-supported fungal network graph with:

- total nodes
- total edges
- average degree
- isolated nodes
- most connected taxa or locations
- clickable graph nodes
- an educational signal pulse animation
