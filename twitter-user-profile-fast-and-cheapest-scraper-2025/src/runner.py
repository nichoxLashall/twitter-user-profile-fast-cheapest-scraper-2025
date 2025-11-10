import argparse
import json
import logging
import sys
from pathlib import Path
from typing import List, Optional

from extractors.twitter_parser import TwitterProfileExtractor
from outputs.exporters import export_data
from outputs.exporters import ExportFormat

def configure_logging(level_name: str) -> None:
    level = getattr(logging, level_name.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )

def load_config(config_path: Path) -> dict:
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at: {config_path}")

    with config_path.open("r", encoding="utf-8") as f:
        config = json.load(f)

    if not isinstance(config, dict):
        raise ValueError("Config file must contain a JSON object at the top level.")

    return config

def read_input_identifiers(path: Path) -> List[str]:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found at: {path}")

    identifiers: List[str] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            identifiers.append(line)

    if not identifiers:
        logging.warning("No identifiers found in input file.")
    else:
        logging.info("Loaded %d identifiers from %s", len(identifiers), path)

    return identifiers

def parse_args(base_dir: Path) -> argparse.Namespace:
    default_input = base_dir / "data" / "inputs.sample.txt"
    default_output = base_dir / "data" / "output.json"
    default_config = base_dir / "src" / "config" / "settings.example.json"

    parser = argparse.ArgumentParser(
        description="Twitter User Profile Fast & Cheapest Scraper 2025 (mock implementation)."
    )
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        default=str(default_input),
        help=f"Path to input usernames/URLs file (default: {default_input})",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=str(default_output),
        help=f"Path to output file (default: {default_output})",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=[fmt.value for fmt in ExportFormat],
        default=ExportFormat.JSON.value,
        help="Output format: json or csv (default: json)",
    )
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        default=str(default_config),
        help=f"Path to configuration JSON (default: {default_config})",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Also print the resulting data to STDOUT.",
    )
    return parser.parse_args()

def main(argv: Optional[List[str]] = None) -> int:
    base_dir = Path(__file__).resolve().parent.parent
    args = parse_args(base_dir)

    try:
        config = load_config(Path(args.config))
    except Exception as exc:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        )
        logging.error("Failed to load configuration: %s", exc)
        return 1

    log_level = config.get("log_level", "INFO")
    configure_logging(log_level)

    logger = logging.getLogger("runner")

    try:
        identifiers = read_input_identifiers(Path(args.input))
    except Exception as exc:
        logger.error("Failed to read input identifiers: %s", exc)
        return 1

    if not identifiers:
        logger.error("No usable identifiers found. Aborting.")
        return 1

    extractor = TwitterProfileExtractor(config=config, base_dir=base_dir)

    logger.info("Fetching profiles for %d identifiers...", len(identifiers))
    profiles = extractor.fetch_profiles(identifiers)

    if not profiles:
        logger.warning("No profiles resolved from the provided identifiers.")
    else:
        logger.info("Resolved %d profiles.", len(profiles))

    output_path = Path(args.output)
    try:
        export_data(
            profiles,
            ExportFormat(args.format),
            output_path=output_path,
            also_stdout=args.stdout,
        )
    except Exception as exc:
        logger.error("Failed to export data: %s", exc)
        return 1

    logger.info("Completed successfully.")
    return 0

if __name__ == "__main__":
    sys.exit(main())