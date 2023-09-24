import os
from pathlib import Path

from openmht import cli


# Get the root directory of the project
ROOT_DIR = str(Path(__file__).parent.parent)

# Get the path to the test data
TEST_DATA_PATH = os.path.join(ROOT_DIR, "SampleData")
TEST_FILE_PATH = os.path.join(TEST_DATA_PATH, "SampleInput.csv")
PARAM_FILE_PATH = os.path.join(ROOT_DIR, "params.txt")
OUTDIR = os.path.join(ROOT_DIR, "tests", "output")
OUT_FILE_PATH = os.path.join(OUTDIR, "output.csv")
TRUTH_FILE_PATH = os.path.join(TEST_DATA_PATH, "SampleOutput.csv")

# Make the output directory if it doesn't exist
if not os.path.exists(OUTDIR):
    os.makedirs(OUTDIR)


def test_basic():
    """Test basic MHT functionality on sample data."""

    # Create the list of parameters
    command_line_args = [TEST_FILE_PATH, OUT_FILE_PATH, PARAM_FILE_PATH]

    # Run MHT on the sample data
    cli.run(command_line_args)

    # Verify the output
    
    # Compare the output to the truth
    with open(OUT_FILE_PATH, "r", encoding="utf-8") as f:
        output = f.readlines()
        
    with open(TRUTH_FILE_PATH, "r", encoding="utf-8") as f:
        truth = f.readlines()

    # Compare the output to the truth
    for i, line in enumerate(output):
        assert line == truth[i]
    