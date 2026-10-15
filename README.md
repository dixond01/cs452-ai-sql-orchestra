# Youth Orchestra

My project models a paid youth music program: its ensembles (symphony, wind ensemble, string quartet, ...), the conductor of each one, the players and their parents, and which section and chair each player sits in for each ensemble. Players can be in several ensembles (as long as the rehearsals don't overlap) and can play a different instrument in each one.

<img src="schema.png">

## Model

I ran everything on **`openai/gpt-oss-120b`** (OpenAI's open-weight GPT model) through Groq's free API, because my cards were declined when buying OpenAI credits. I first tried Gemini (`gemini-3.8-flash`), but its free tier allows only 20 requests a day per model, which ran out partway through the zero-shot run. Total cost: $0.

All 11 questions were run under all three prompting strategies (66 requests). The logs are in [`responses/`](responses/), and more examples are in [examples.md](examples.md).

## Query it did well on

**Question**: Which conductor works with the most players?

This one needs `COUNT(DISTINCT ...)`: several players are in two ensembles with the same conductor, so a plain count would say Maria Alvarez works with 16 players instead of 11.

**SQL** (zero-shot):
```sql
WITH conductor_player_counts AS (
    SELECT
        c.conductor_id,
        c.name,
        c.email,
        COUNT(DISTINCT m.player_id) AS player_count
    FROM conductor AS c
    JOIN ensemble   AS e ON c.conductor_id = e.conductor_id
    JOIN membership AS m ON e.ensemble_id = m.ensemble_id
    GROUP BY c.conductor_id
)
SELECT
    conductor_id,
    name,
    email,
    player_count
FROM conductor_player_counts
WHERE player_count = (SELECT MAX(player_count) FROM conductor_player_counts);
```

**Result**: `[(1, 'Maria Alvarez', 'malvarez@valleyyouthmusic.org', 11)]`

**Friendly response**: Maria Alvarez (malvarez@valleyyouthmusic.org) works with the most players—11 in total.

All three strategies got this right.

## Question that it tripped up on

**Question**: We need to email the parents of everyone in the Jazz Band. Is there anyone we can't reach?

**SQL** (zero-shot):
```sql
SELECT p.parent_id, p.name, p.email
FROM parent AS p
JOIN player_parent AS pp ON p.parent_id = pp.parent_id
JOIN player AS pl ON pp.player_id = pl.player_id
JOIN membership AS m ON pl.player_id = m.player_id
JOIN ensemble AS e ON m.ensemble_id = e.ensemble_id
WHERE e.name = 'Jazz Band'
  AND (p.email IS NULL OR p.email = '');
```

**Result**: `[(7, 'Carlos Martinez', None)]`

**Friendly response**: Yes—parent Carlos Martinez (ID 7) has no email address on file.

This sounds right, but it's incomplete. Benjamin Lee plays bass in the Jazz Band and has **no parent on file at all**, so we can't email anyone for him either. The query starts from the `parent` table and uses inner joins, so a player with no parent row never shows up. All three strategies made the same mistake, and the friendly answer sounds confident, so a user would have no way of knowing someone was missed.

## Prompting strategies

I tried all three strategies from [the paper](https://arxiv.org/abs/2305.11853). Every prompt includes the `CREATE TABLE` statements plus 3 sample rows from each table, which the paper found works best.

- **Zero-shot**: just the schema, sample rows and the question.
- **Single-domain**: adds 3 example questions with SQL written for my orchestra database.
- **Cross-domain**: adds 3 example questions with SQL for a different database (the dog show example from class), then my database.

| Strategy | SQL that answered the question correctly (out of 11) |
|---|---|
| Zero-shot | 10 |
| Single-domain | 9 |
| Cross-domain | 10 |

There was very little difference. All three missed the parent-email question above. The only other miss was single-domain on my own question, "Do any orchestras have the same conductor?" It took "orchestras" literally and only looked at ensembles with "Orchestra" in the name (just the Symphony Orchestra), so it answered "Nothing matched." The other two strategies treated orchestras as all ensembles and correctly found Maria Alvarez and David Chen each conducting two. My guess is the single-domain examples, which filter on exact ensemble names like `'Jazz Band'`, nudged it toward matching names literally.

The examples did change the *style* of the SQL: with single-domain examples, the queries used the same aliases and column naming as my examples. The paper found examples help most on harder, larger benchmarks; my database is small and the model is much newer than the ones in the paper, so zero-shot was already nearly perfect.

## Conclusion

The model is very good at writing SQL for a small, clean schema, including self-joins for overlapping rehearsal times and `DISTINCT` counts. The risky part is the friendly answer: when the SQL is subtly incomplete or an empty result is correct, the response sounds just as confident as when it's right ("Nothing matched" for Emma Larsen gives no hint *why*: every other ensemble conflicts with one she's already in). For engineers who can read the SQL this is a useful tool, but for non-technical users it could give wrong answers without any warning.

## How to run

1. `python -m venv .venv` and `.venv\Scripts\pip install -r requirements.txt`
2. Copy `config.example.json` to `config.json` and paste in your own API key. The example is set up for Groq (free key from console.groq.com). Any OpenAI-compatible provider works: for OpenAI itself, delete the `baseUrl` line and set `model` to an OpenAI model such as `gpt-4o-mini`. Run `python ai.py` to check the key.
3. `python chat.py` to ask questions interactively, or `python run_experiments.py` to run every question under all three prompting strategies (logs are written to `responses/`).

## Files

- `setup.sql` / `setupData.sql`: the tables and the mock data.
- `db.py`: builds `aidb.sqlite` and runs read-only queries.
- `ai.py`: the prompting strategies and the API calls.
- `prompt_examples.py`: the example question/SQL pairs for the few-shot strategies.
- `chat.py`: the interactive app.
- `run_experiments.py`: the batch run over all questions and strategies.
- `make_schema_picture.py`: draws `schema.png` from the database.
- `examples.md`: more question / SQL / response examples.
