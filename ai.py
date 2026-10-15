"""Talks to OpenAI: turns a question into SQL, and SQL results into a plain-English answer."""
import json
import os

from openai import OpenAI, RateLimitError

import db
from prompt_examples import (
    CROSS_DOMAIN_EXAMPLES,
    CROSS_DOMAIN_SCHEMA,
    SINGLE_DOMAIN_EXAMPLES,
)

CONFIG_PATH = db.get_path("config.json")
DEFAULT_MODEL = "gpt-4o-mini"

_client = None
_model = DEFAULT_MODEL


def get_client():
    """Create the client from config.json the first time it is needed.

    Works with OpenAI, or with any provider that offers an OpenAI-compatible
    endpoint (such as Gemini) when "baseUrl" is set in config.json.
    """
    global _client, _model
    if _client is None:
        if not os.path.exists(CONFIG_PATH):
            raise SystemExit("config.json not found. Copy config.example.json to config.json and paste in your API key.")
        with open(CONFIG_PATH, encoding="utf-8-sig") as f:  # -sig: tolerate a BOM from Windows editors
            config = json.load(f)
        api_key = config.get("apiKey") or config.get("openaiKey", "")
        if not api_key or "PASTE" in api_key:
            raise SystemExit("config.json does not contain an API key yet. Paste yours into the \"apiKey\" field.")
        _model = config.get("model", DEFAULT_MODEL)
        # max_retries waits and retries when a free tier's per-minute limit is hit
        _client = OpenAI(api_key=api_key, base_url=config.get("baseUrl"), max_retries=4)
    return _client


def get_model():
    get_client()
    return _model


class QuotaExhausted(Exception):
    """The daily quota is used up, so retrying today won't help."""


def ask_gpt(content):
    try:
        response = get_client().chat.completions.create(
            model=_model,
            messages=[{"role": "user", "content": content}],
        )
    except RateLimitError as err:
        if "perday" in str(err).lower().replace(" ", ""):
            raise QuotaExhausted(f"Daily request limit reached for {_model}.") from err
        raise
    return response.choices[0].message.content


# ---------------------------------------------------------------------------
# Prompting strategies
# ---------------------------------------------------------------------------

SQL_ONLY_REQUEST = (
    "Give me a sqlite select statement that answers the question. "
    "Only respond with sqlite syntax. If there is an error do not explain it!"
)


def _format_examples(examples):
    return "\n\n".join(f"Question: {e['question']}\n{e['sql']}" for e in examples)


def _our_database():
    return db.read_schema() + "\n\n" + db.sample_rows()


def zero_shot_prefix():
    # instruction + our database, no examples
    return _our_database() + "\n\n" + SQL_ONLY_REQUEST


def single_domain_prefix():
    # our database + example questions answered against our database
    return (
        _our_database()
        + "\n\nHere are example questions about this database and the sqlite that answers them:\n\n"
        + _format_examples(SINGLE_DOMAIN_EXAMPLES)
        + "\n\n" + SQL_ONLY_REQUEST
    )


def cross_domain_prefix():
    # a different database with its example questions, then our database
    return (
        "Here is an example database:\n\n"
        + CROSS_DOMAIN_SCHEMA
        + "\n\nHere are example questions about that database and the sqlite that answers them:\n\n"
        + _format_examples(CROSS_DOMAIN_EXAMPLES)
        + "\n\nNow here is a different database. Answer the question about this one:\n\n"
        + _our_database()
        + "\n\n" + SQL_ONLY_REQUEST
    )


STRATEGIES = {
    "zero_shot": zero_shot_prefix,
    "single_domain": single_domain_prefix,
    "cross_domain": cross_domain_prefix,
}


# ---------------------------------------------------------------------------
# Question -> SQL -> rows -> friendly answer
# ---------------------------------------------------------------------------

def sanitize_for_just_sql(value):
    """GPT often wraps SQL in ```sql ... ``` markdown. Keep only what is inside."""
    marker = "```"
    if marker in value:
        value = value.split(marker, 1)[1]
        newline_index = value.find("\n")  # skip the language tag (sql, sqlite, ...)
        if newline_index != -1:
            value = value[newline_index + 1:]
    if marker in value:
        value = value.split(marker, 1)[0]
    return value.strip()


def get_sql(question, strategy):
    prompt = STRATEGIES[strategy]() + "\n\nQuestion: " + question
    return sanitize_for_just_sql(ask_gpt(prompt))


def get_friendly_answer(question, sql, columns, rows):
    prompt = (
        "This is the schema of my sqlite database:\n\n" + db.read_schema()
        + "\n\nI asked this question: \"" + question + "\"\n\n"
        + "To answer it, this query was run:\n\n" + sql
        + "\n\nIt returned these columns: " + str(columns)
        + "\nand these rows: " + str(rows)
        + "\n\nAnswer my question in a concise, friendly way using only that data. "
        + "If no rows came back, say that nothing matched. "
        + "Please do not give any other suggestions or chatter."
    )
    return ask_gpt(prompt)


def answer_question(question, strategy="zero_shot"):
    """Run the whole pipeline. Always returns a dict; failures are recorded under 'error'."""
    result = {
        "question": question,
        "sql": "",
        "queryRawResponse": "",
        "friendlyResponse": "",
        "error": "None",
    }
    try:
        result["sql"] = get_sql(question, strategy)
        columns, rows = db.run_sql(result["sql"])
        result["queryRawResponse"] = str(rows)
        result["friendlyResponse"] = get_friendly_answer(question, result["sql"], columns, rows)
    except QuotaExhausted:
        raise  # stop the whole run instead of failing every remaining question
    except Exception as err:
        result["error"] = str(err)
    return result


if __name__ == "__main__":
    # Key check: lists the models this key can use, then asks one tiny question.
    print("Models available to this key:")
    for model in get_client().models.list():
        print("  " + model.id)
    print(f"\nUsing model {get_model()}: " + ask_gpt("Reply with just the word: working"))
