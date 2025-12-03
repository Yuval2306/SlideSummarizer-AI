import os
import json
import asyncio
import argparse
from pathlib import Path

from ppt_parser import parse_presentation
from gemini_client import process_slides


async def main(ppt_file_path):
    """Main function to process a PowerPoint file."""
    print(f"Parsing presentation: {ppt_file_path}")
    slides = await parse_presentation(ppt_file_path)

    if not slides:
        print("No slides with text found in the presentation.")
        return

    print(f"Found {len(slides)} slides with text. Processing...")

    explanations = await process_slides(slides)

    output_file = Path(ppt_file_path).with_suffix(".json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(explanations, f, indent=2, ensure_ascii=False)

    print(f"Explanations saved to {output_file}")


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Explain PowerPoint slides using Gemini AI")
        parser.add_argument("file", help="Path to the PowerPoint file (.pptx)")
        args = parser.parse_args()

        if not os.path.exists(args.file):
            print(f"Error: File '{args.file}' does not exist.")
            exit(1)

        print(f"Processing file: {args.file}")
        asyncio.run(main(args.file))
    except Exception as e:
        print(f"Error: {e}")