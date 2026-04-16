"""
export.py — Export the enriched SQLite data to output/research_output.csv.

This script will:
  1. JOIN the `apps` table with the `classifications` table produced by classify.py
  2. Select the columns relevant for the research output (dropping raw_json and
     other large blobs)
  3. Write the result to output/research_output.csv using pandas
"""


def main():
    # TODO: implement export logic
    pass


if __name__ == "__main__":
    main()
