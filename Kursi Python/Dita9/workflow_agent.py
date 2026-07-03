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


def normalize_notes(saved_notes):
    normalized_notes = []

    for note in saved_notes:
        if not isinstance(note, dict):
            continue

        normalized_notes.append(
            {
                "text": note.get("text", ""),
                "created_at": note.get("created_at", note.get("saved_at", "")),
                "done": note.get("done", False),
            }
        )

    return normalized_notes


history = load_json_file(HISTORY_FILE)
notes = normalize_notes(load_json_file(NOTES_FILE))


def detect_intent(user_input):
    text = user_input.lower().strip()

    if text in {"exit", "quit", "dal"}:
        return "exit"

    if text in {"help", "ndihme"}:
        return "help"

    if text.startswith("shto detyre:") or text.startswith("ruaj shenim:"):
        return "add_task"

    if text in {"shfaq detyrat", "shfaq shenimet"}:
        return "show_tasks"

    if text.startswith("planifiko:"):
        return "plan"

    if text.startswith("kontrollo tekstin:"):
        return "check_text"

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


def add_note_tool(note_text):
    clean_note = note_text.strip()

    if not clean_note:
        return "Shenimi eshte bosh. Shkruaj dicka pas ':'"

    notes.append(
        {
            "text": clean_note,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "done": False,
        }
    )
    save_json_file(NOTES_FILE, notes)
    return f"Shenimi u ruajt: {clean_note}"


def show_notes_tool():
    if not notes:
        return "Nuk ka ende shenime."

    lines = []
    for index, note in enumerate(notes, start=1):
        status = "DONE" if note["done"] else "TODO"
        lines.append(f"{index}. [{status}] {note['text']} ({note['created_at']})")

    return "\n".join(lines)


def planner_tool(goal):
    clean_goal = goal.strip()

    if not clean_goal:
        return "Shkruaj nje qellim pas ':'"

    steps = [
        f"Percakto qellimin: {clean_goal}",
        "Ndaje qellimin ne hapa te vegjel.",
        "Zgjidh tool-in ose veprimin per secilin hap.",
        "Ekzekuto hapat me radhe.",
        "Kontrollo rezultatin dhe permireso nese duhet.",
    ]

    return "\n".join(f"{index}. {step}" for index, step in enumerate(steps, start=1))


def text_checker_tool(text):
    words = text.split()
    character_count = len(text)
    word_count = len(words)

    if word_count == 0:
        return "Teksti eshte bosh."

    average_word_length = character_count / word_count

    return (
        f"Numri i fjaleve: {word_count}\n"
        f"Numri i karaktereve: {character_count}\n"
        f"Gjatesia mesatare e fjales: {average_word_length:.1f}"
    )


def add_to_history(user_input, response):
    history.append(
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "input": user_input,
            "response": response,
        }
    )
    save_json_file(HISTORY_FILE, history)


def build_response(intent, tool_used, result, plan=None):
    return {
        "intent": intent,
        "tool_used": tool_used,
        "plan": plan or [],
        "result": result,
    }


def agent_response(user_input):
    intent = detect_intent(user_input)

    if intent == "exit":
        response = build_response(
            intent,
            None,
            "Duke e mbyllur Workflow Agent. Suksese ne ushtrime!",
        )
    elif intent == "help":
        response = build_response(
            intent,
            None,
            (
                "Provo keto komanda:\n"
                "- planifiko: meso Python per provim\n"
                "- shto detyre: ushtro funksionet\n"
                "- ruaj shenim: perserit AI Agents\n"
                "- shfaq detyrat\n"
                "- shfaq shenimet\n"
                "- kontrollo tekstin: Une po mesoj AI Agents\n"
                "- llogarit 25 * 4\n"
                "- history\n"
                "- exit"
            ),
        )
    elif intent == "add_task":
        task_text = user_input.split(":", 1)[1]
        response = build_response(
            intent,
            "add_note_tool",
            add_note_tool(task_text),
            ["Lexo tekstin pas ':'", "Ruaje shenimin ne notes.json", "Kthe konfirmim"],
        )
    elif intent == "show_tasks":
        response = build_response(
            intent,
            "show_notes_tool",
            show_notes_tool(),
            ["Lexo notes.json", "Formatizo listen", "Shfaq rezultatin"],
        )
    elif intent == "plan":
        goal = user_input.split(":", 1)[1]
        response = build_response(
            intent,
            "planner_tool",
            planner_tool(goal),
            ["Merr qellimin", "Krijo hapa", "Kthe planin final"],
        )
    elif intent == "check_text":
        text = user_input.split(":", 1)[1].strip()
        response = build_response(
            intent,
            "text_checker_tool",
            text_checker_tool(text),
            ["Lexo tekstin", "Numero fjalet", "Llogarit statistika"],
        )
    elif intent == "math":
        expression = user_input.lower().replace("llogarit", "").strip()
        response = build_response(
            intent,
            "calculator_tool",
            calculator_tool(expression),
            ["Nxirr shprehjen matematike", "Verifiko karakteret", "Llogarit rezultatin"],
        )
    else:
        response = build_response(
            intent,
            None,
            "Nuk e kuptova kerkesen. Shkruaj 'help' per komandat.",
        )

    add_to_history(user_input, response)
    return response


def print_response(response):
    print("\n--- Workflow Agent ---")
    print(f"Intent: {response['intent']}")
    print(f"Tool: {response['tool_used']}")

    if response["plan"]:
        print("Plani:")
        for index, step in enumerate(response["plan"], start=1):
            print(f"  {index}. {step}")

    print(f"Rezultati:\n{response['result']}")
    print("-" * 35)


def print_history():
    print("\n--- History ---")
    if not history:
        print("Nuk ka ende histori.")
        return

    for index, item in enumerate(history, start=1):
        print(f"{index}. [{item['timestamp']}] {item['input']}")
        print(f"   Intent: {item['response']['intent']}")
        print(f"   Tool: {item['response']['tool_used']}")


def main():
    print("Workflow Agent u nis.")
    print("Shkruaj 'help' per komandat.")

    while True:
        user_input = input("\nShkruaj kerkesen tende: ").strip()

        if not user_input:
            print("Te lutem shkruaj nje kerkese.")
            continue

        if user_input.lower() == "history":
            print_history()
            continue

        response = agent_response(user_input)
        print_response(response)

        if response["intent"] == "exit":
            break


if __name__ == "__main__":
    main()
