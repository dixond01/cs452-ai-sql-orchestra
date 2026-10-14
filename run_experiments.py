"""Runs every question under every prompting strategy and saves a JSON log per strategy."""
import json
import os
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
    db.build_db()
    os.makedirs(db.get_path("responses"), exist_ok=True)
    print(f"Model: {ai.get_model()}")

    for strategy in ai.STRATEGIES:
        print("########################################################################")
        print(f"Running strategy: {strategy}")
        responses = {
            "strategy": strategy,
            "model": ai.get_model(),
            "prompt_prefix": ai.STRATEGIES[strategy](),
        }
        question_results = []
        for question in QUESTIONS:
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print("Question:\n" + question)
            result = ai.answer_question(question, strategy)
            print("SQL:\n" + result["sql"])
            print("Raw result:\n" + result["queryRawResponse"])
            print("Friendly response:\n" + result["friendlyResponse"])
            if result["error"] != "None":
                print("Error:\n" + result["error"])
            question_results.append(result)

        responses["questionResults"] = question_results
        out_path = db.get_path(os.path.join("responses", f"response_{strategy}_{time()}.json"))
        with open(out_path, "w") as out_file:
            json.dump(responses, out_file, indent=2)
        print(f"Saved {out_path}")

    print("Done!")


if __name__ == "__main__":
    main()
