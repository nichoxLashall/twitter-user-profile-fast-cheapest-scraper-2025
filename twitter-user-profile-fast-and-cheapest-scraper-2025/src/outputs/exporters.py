import csv
import json
import logging
from enum import Enum
from pathlib import Path
from typing import Iterable, List, Mapping, Any

logger = logging.getLogger(__name__)

class ExportFormat(str, Enum):
    JSON = "json"
    CSV = "csv"

def _ensure_parent_dir(path: Path) -> None:
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)

def export_to_json(records: Iterable[Mapping[str, Any]], output_path: Path) -> None:
    data = list(records)
    _ensure_parent_dir(output_path)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info("Wrote %d records to JSON file %s", len(data), output_path)

def export_to_csv(records: Iterable[Mapping[str, Any]], output_path: Path) -> None:
    records_list: List[Mapping[str, Any]] = list(records)
    if not records_list:
        logger.warning("No records to export; writing an empty CSV file to %s", output_path)
        _ensure_parent_dir(output_path)
        with output_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([])
        return

    # Build a stable header from the union of keys across records
    header_keys = sorted({key for record in records_list for key in record.keys()})

    _ensure_parent_dir(output_path)
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header_keys, extrasaction="ignore")
        writer.writeheader()
        for record in records_list:
            writer.writerow({k: record.get(k, "") for k in header_keys})

    logger.info("Wrote %d records to CSV file %s", len(records_list), output_path)

def export_to_stdout(records: Iterable[Mapping[str, Any]]) -> None:
    data = list(records)
    print(json.dumps(data, ensure_ascii=False, indent=2))

def export_data(
    records: Iterable[Mapping[str, Any]],
    export_format: ExportFormat,
    output_path: Path,
    also_stdout: bool = False,
) -> None:
    """
    Dispatch export to the appropriate format handler and optionally print to STDOUT.
    """
    records_list: List[Mapping[str, Any]] = list(records)

    if export_format == ExportFormat.JSON:
        export_to_json(records_list, output_path)
    elif export_format == ExportFormat.CSV:
        export_to_csv(records_list, output_path)
    else:
        raise ValueError(f"Unsupported export format: {export_format}")

    if also_stdout:
        export_to_stdout(records_list)