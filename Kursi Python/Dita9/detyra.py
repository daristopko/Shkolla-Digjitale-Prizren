import json
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
HISTORY_FILE = BASE_DIR / "history.json"
NOTES_FILE = BASE_DIR / "notes.json"


def load_json_file(file_path):
    if not file_path.exists():
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, list):
                return data
    except json.JSONDecodeError:
        return []

    return []


def save_json_file(file_path, data):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


history = load_json_file(HISTORY_FILE)
notes = load_json_file(NOTES_FILE)


def show_title(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def explain_step(number, title, description):
    print(f"\nHapi {number}: {title}")
    print("-" * 60)
    print(description)


def detect_intent(user_input):
    text = user_input.lower().strip()

    if text.startswith("ruaj shenim:"):
        return "save_note"

    if text == "shfaq shenimet":
        return "show_notes"

    if text.startswith("planifiko:"):
        return "plan"

    if text.startswith("llogarit"):
        return "math"

    return "general"


def calculator_tool(expression):
    allowed_chars = "0123456789+-*/(). "

    if not all(char in allowed_chars for char in expression):
        return "Shprehja permban karaktere qe nuk lejohen."

    try:
        return eval(expression, {"__builtins__": {}}, {})
    except Exception as error:
        return f"Gabim ne llogaritje: {error}"


def save_note_tool(note_text):
    clean_note = note_text.strip()

    if not clean_note:
        return "Shenimi eshte bosh."

    note = {
        "text": clean_note,
        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    notes.append(note)
    save_json_file(NOTES_FILE, notes)
    return f"Shenimi u ruajt ne notes.json: {clean_note}"


def show_notes_tool():
    if not notes:
        return "Nuk ka ende shenime ne notes.json."

    lines = []
    for index, note in enumerate(notes, start=1):
        saved_at = note.get("saved_at", note.get("created_at", "pa date"))
        lines.append(f"{index}. {note.get('text', '')} ({saved_at})")

    return "\n".join(lines)


def planner_tool(goal):
    clean_goal = goal.strip()

    if not clean_goal:
        return "Nuk ka qellim per planifikim."

    steps = [
        f"Kupto qellimin: {clean_goal}",
        "Ndaje qellimin ne detyra te vogla.",
        "Zgjidh cilat tools duhen perdorur.",
        "Ekzekuto hapat nje nga nje.",
        "Ruaj rezultatin ne history.json.",
    ]

    return "\n".join(f"{index}. {step}" for index, step in enumerate(steps, start=1))


def save_history(user_input, intent, tool_used, result):
    item = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "input": user_input,
        "response": {
            "intent": intent,
            "tool_used": tool_used,
            "result": result,
        },
    }

    history.append(item)
    save_json_file(HISTORY_FILE, history)


def explain_agent_flow(user_input):
    show_title("DEMO: Si punon nje AI Agent me workflow")

    explain_step(
        1,
        "Input",
        f"Perdoruesi shkruan kete kerkese:\n\n{user_input}",
    )

    intent = detect_intent(user_input)
    explain_step(
        2,
        "Intent",
        (
            "Agjenti mundohet ta kuptoje qellimin e perdoruesit.\n"
            f"Intent-i i zbuluar eshte: {intent}"
        ),
    )

    plan = [
        "Lexo kerkesen e perdoruesit.",
        "Gjej intent-in.",
        "Zgjidh tool-in e duhur.",
        "Ekzekuto tool-in.",
        "Ruaj veprimin ne history.json.",
    ]

    explain_step(
        3,
        "Plan",
        "\n".join(f"{index}. {step}" for index, step in enumerate(plan, start=1)),
    )

    tool_used = None

    if intent == "save_note":
        note_text = user_input.split(":", 1)[1]
        tool_used = "save_note_tool"
        result = save_note_tool(note_text)
    elif intent == "show_notes":
        tool_used = "show_notes_tool"
        result = show_notes_tool()
    elif intent == "plan":
        goal = user_input.split(":", 1)[1]
        tool_used = "planner_tool"
        result = planner_tool(goal)
    elif intent == "math":
        expression = user_input.lower().replace("llogarit", "").strip()
        tool_used = "calculator_tool"
        result = calculator_tool(expression)
    else:
        result = "Nuk u gjet tool i vecante per kete kerkese."

    explain_step(
        4,
        "Tool",
        (
            "Tool eshte funksioni qe e kryen punen konkrete.\n"
            f"Tool-i i perdorur: {tool_used}"
        ),
    )

    explain_step(
        5,
        "Result",
        f"Rezultati final eshte:\n\n{result}",
    )

    save_history(user_input, intent, tool_used, result)

    explain_step(
        6,
        "JSON",
        (
            "Ne fund, agjenti ruan veprimin ne history.json.\n"
            "Nese ishte shenim, e ruan edhe ne notes.json.\n"
            "Kjo quhet persistence: te dhenat nuk humbin kur programi mbyllet."
        ),
    )


def run_examples():
    examples = [
        "planifiko: meso Python dhe AI Agents",
        "ruaj shenim: Sot mesuam workflow dhe JSON",
        "shfaq shenimet",
        "llogarit 24 * 3",
    ]

    show_title("Shembuj per shpjegim ne klase")

    for index, example in enumerate(examples, start=1):
        print(f"{index}. {example}")

    print("\nZgjidh nje shembull duke shkruar numrin 1-4.")
    print("Ose shkruaj kerkesen tende.")

    user_choice = input("\nZgjedhja jote: ").strip()

    if user_choice in {"1", "2", "3", "4"}:
        selected_input = examples[int(user_choice) - 1]
    else:
        selected_input = user_choice

    if not selected_input:
        selected_input = examples[0]

    explain_agent_flow(selected_input)


def main():
    show_title("Spjegim Interaktiv: AI Agent + Workflow + JSON")
    print("Ky file eshte per shpjegim me nxenesit.")
    print("Ai nuk jep vetem rezultat, por tregon hapat si mendon agenti.")

    while True:
        run_examples()

        again = input("\nDeshiron ta provosh edhe nje here? (po/jo): ").lower().strip()
        if again not in {"po", "p", "yes", "y"}:
            print("\nFaleminderit! Tani mund te kontrollosh history.json dhe notes.json.")
            break


if __name__ == "__main__":
    main()
