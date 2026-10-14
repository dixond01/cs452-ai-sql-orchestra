"""Interactive app: ask the database questions in plain English."""
import ai
import db


def main():
    db.build_db()
    strategy = "zero_shot"
    print(f"Ask a question about the database. Model: {ai.get_model()}")
    print("Commands:  /strategy <" + " | ".join(ai.STRATEGIES) + ">   /quit")

    while True:
        try:
            question = input(f"\n[{strategy}] > ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not question:
            continue
        if question in ("/quit", "/exit"):
            break
        if question.startswith("/strategy"):
            choice = question.split()[-1]
            if choice in ai.STRATEGIES:
                strategy = choice
            else:
                print("Strategies: " + ", ".join(ai.STRATEGIES))
            continue

        result = ai.answer_question(question, strategy)
        print("\nSQL:\n" + result["sql"])
        if result["error"] != "None":
            print("\nError: " + result["error"])
            continue
        print("\nRaw result:\n" + result["queryRawResponse"])
        print("\nAnswer:\n" + result["friendlyResponse"])


if __name__ == "__main__":
    main()
