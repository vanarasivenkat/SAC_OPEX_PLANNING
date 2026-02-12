#!/usr/bin/env python3
"""
CoolSnail Technologies - Standardized Resume Generator

Reads candidate resume data from a JSON file, validates it against
the schema, renders it into a branded HTML template, and exports
the result as a PDF.

Usage:
    python generate_resume.py <candidate_data.json> [--output <output_path.pdf>]
    python generate_resume.py --html-only <candidate_data.json>  # outputs HTML instead of PDF

Examples:
    python generate_resume.py sample_data/sample_candidate.json
    python generate_resume.py sample_data/sample_candidate.json --output john_doe_resume.pdf
    python generate_resume.py --html-only sample_data/sample_candidate.json > resume.html
"""

import argparse
import json
import os
import sys

from jinja2 import Environment, FileSystemLoader

from resume_schema import validate_resume_data


TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")


def load_candidate_data(json_path):
    """Load and parse candidate JSON data from file."""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def render_html(data):
    """Render candidate data into the HTML resume template."""
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=True)
    template = env.get_template("resume_template.html")
    return template.render(**data)


def generate_pdf(html_content, output_path):
    """Convert rendered HTML to PDF using WeasyPrint."""
    from weasyprint import HTML

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    HTML(string=html_content).write_pdf(output_path)
    return output_path


def build_output_filename(data, output_dir):
    """Build a default output filename from the candidate's name."""
    safe_name = data["candidate_name"].replace(" ", "_").lower()
    return os.path.join(output_dir, f"{safe_name}_resume.pdf")


def main():
    parser = argparse.ArgumentParser(
        description="CoolSnail Technologies - Standardized Resume Generator"
    )
    parser.add_argument(
        "input_json",
        help="Path to candidate data JSON file",
    )
    parser.add_argument(
        "--output", "-o",
        help="Output PDF file path (default: output/<candidate_name>_resume.pdf)",
    )
    parser.add_argument(
        "--html-only",
        action="store_true",
        help="Output rendered HTML to stdout instead of generating PDF",
    )

    args = parser.parse_args()

    # Load data
    try:
        data = load_candidate_data(args.input_json)
    except FileNotFoundError:
        print(f"Error: File not found: {args.input_json}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.input_json}: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate
    is_valid, errors = validate_resume_data(data)
    if not is_valid:
        print("Validation errors:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)

    # Render HTML
    html_content = render_html(data)

    if args.html_only:
        print(html_content)
        return

    # Generate PDF
    output_path = args.output or build_output_filename(data, OUTPUT_DIR)
    generate_pdf(html_content, output_path)
    print(f"Resume generated: {output_path}")


if __name__ == "__main__":
    main()
