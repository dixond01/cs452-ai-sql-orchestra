# Youth Orchestra

This database represents a fictional youth orchestra program. It is meant for managing players, their parents, conductors, and their positions in the ensembles. It does not handle tuition, salaries, or billing.

<img src="schema.png">

Questions in plain English are turned into SQL by an AI model, run against the database, and the results are turned back into a plain-English answer. Results were generated with `openai/gpt-oss-120b` through Groq's free API. Example questions, SQL and responses are in [examples.md](examples.md), and the full logs are in [`responses/`](responses/).

## How to run

1. `python -m venv .venv` and `.venv\Scripts\pip install -r requirements.txt`
2. Copy `config.example.json` to `config.json` and paste in your own API key. The example is set up for Groq (free key from console.groq.com). Any OpenAI-compatible provider works: for OpenAI itself, delete the `baseUrl` line and set `model` to an OpenAI model such as `gpt-4o-mini`. Run `python ai.py` to check the key.
3. `python chat.py` to ask questions interactively, or `python run_experiments.py` to run every question under all three prompting strategies (zero-shot, single-domain, cross-domain). Logs are written to `responses/`.

## Files

- `setup.sql` / `setupData.sql`: the tables and the mock data.
- `db.py`: builds `aidb.sqlite` and runs read-only queries.
- `ai.py`: the prompting strategies and the API calls.
- `prompt_examples.py`: the example question/SQL pairs for the few-shot strategies.
- `chat.py`: the interactive app.
- `run_experiments.py`: the batch run over all questions and strategies.
- `make_schema_picture.py`: draws `schema.png` from the database.
- `examples.md`: question / SQL / response examples.
