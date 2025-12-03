import os
import json
import pytest
import asyncio
from pathlib import Path

from main import main


@pytest.mark.asyncio
async def test_presentation_processing():
    """Test that the script can process a presentation and generate an output file."""
    # Path to the test presentation in the same directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_pptx = os.path.join(current_dir, "KidSafe.pptx")

    assert os.path.exists(test_pptx), f"Test file {test_pptx} not found"

    await main(test_pptx)

    output_file = Path(test_pptx).with_suffix(".json")
    assert os.path.exists(output_file), f"Output file {output_file} was not created"

    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert len(data) > 0, "No explanations were generated"

    for item in data:
        assert "slide_number" in item, "Missing slide_number in output"
        assert "explanation" in item, "Missing explanation in output"