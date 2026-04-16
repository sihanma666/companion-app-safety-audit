"""
classify.py — Classify each app in companion_apps.db using the Claude API.

For each row in the `apps` table, this script will:
  1. Build a prompt from key fields (title, description, genre, content_rating, etc.)
  2. Send the prompt to Claude and ask it to classify the app across a set of
     research dimensions (e.g. is it an AI companion, does it target minors,
     does it monetise emotional dependency, etc.)
  3. Parse Claude's structured response and write the results back into a
     `classifications` table (or additional columns on `apps`).

The Claude API key is read from the ANTHROPIC_API_KEY environment variable
(set in .env and loaded via python-dotenv).
"""


def main():
    # TODO: implement classification logic
    pass


if __name__ == "__main__":
    main()
