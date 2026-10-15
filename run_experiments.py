"""Runs every question under every prompting strategy and saves a JSON log per strategy.

    python run_experiments.py                  all three strategies
    python run_experiments.py single_domain    just the strategies named
"""
import json
import os
import sys
from time import time

import ai
import db

QUESTIONS = [
    "How many players are in each ensemble?",
    "Who is the first chair cellist in the Symphony Orchestra?",
    "Which players play more than one instrument?",
    "Which parents have more than one child in the program?",
    "Which players are not in any ensemble?",
    "Who is the youngest player in the Wind Ensemble?",
    "Which conductor works with the most players?",
    "Which ensembles have rehearsals that overlap in time?",
    "Which other ensembles could Emma Larsen join without a schedule conflict?",
    "We need to email the parents of everyone in the Jazz Band. Is there anyone we can't reach?",
    "Do any orchestras have the same conductor? Which ones?"
]


def main():
    strategies = sys.argv[1:] or list(ai.STRATEGIES)
    for strategy in strategies:
        if strategy not in ai.STRATEGIES:
            raise SystemExit(f"Unknown strategy {strategy}. Choose from: " + ", ".join(ai.STRATEGIES))

    db.build_db()
    os.makedirs(db.get_path("responses"), exist_ok=True)
    print(f"Model: {ai.get_model()}")
    print(f"This run needs up to {len(strategies) * len(QUESTIONS) * 2} requests.")

    for strategy in strategies:
        print("########################################################################")
        print(f"Running strategy: {strategy}")
        responses = {
            "strategy": strategy,
            "model": ai.get_model(),
            "prompt_prefix": ai.STRATEGIES[strategy](),
            "questionResults": [],
        }
        out_path = db.get_path(os.path.join("responses", f"response_{strategy}_{time()}.json"))

        for question in QUESTIONS:
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print("Question:\n" + question)
            try:
                result = ai.answer_question(question, strategy)
            except ai.QuotaExhausted as err:
                print(f"\n{err} Stopping. Results so far are saved in {out_path}")
                return
            print("SQL:\n" + result["sql"])
            print("Raw result:\n" + result["queryRawResponse"])
            print("Friendly response:\n" + result["friendlyResponse"])
            if result["error"] != "None":
                print("Error:\n" + result["error"])

            # save after every question so nothing is lost if the run stops
            responses["questionResults"].append(result)
            with open(out_path, "w") as out_file:
                json.dump(responses, out_file, indent=2)

        print(f"Saved {out_path}")

    print("Done!")


if __name__ == "__main__":
    main()
