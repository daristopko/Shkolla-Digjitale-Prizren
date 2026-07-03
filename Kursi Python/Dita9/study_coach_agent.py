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


def detect_intent(user_input):
    text = user_input.lower().strip()

    if text in {"exit", "quit", "dal"}:
        return "exit"

    if text in {"help", "ndihme"}:
        return "help"

    if text.startswith("krijo plan mesimi:"):
        return "study_plan"

    if text == "kontrollo progresin":
        return "check_progress"

    if text.startswith("ruaj shenim:"):
        return "save_note"

    if text == "shfaq shenimet":
        return "show_notes"

    if text == "fshij shenimet":
        return "delete_notes"

    return "general"


def save_note_tool(note_text):
    clean_note = note_text.strip()

    if not clean_note:
        return "Shenimi eshte bosh. Shkruaj dicka pas ':'"

    notes.append(
        {
            "text": clean_note,
            "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    )
    save_json_file(NOTES_FILE, notes)
    return f"Shenimi u ruajt: {clean_note}"


def show_notes_tool():
    if not notes:
        return "Nuk ka ende shenime ne notes.json."

    lines = []
    for index, note in enumerate(notes, start=1):
        saved_at = note.get("saved_at", note.get("created_at", "pa date"))
        lines.append(f"{index}. {note.get('text', '')} ({saved_at})")

    return "\n".join(lines)


def study_plan_tool(topic):
    clean_topic = topic.strip()

    if not clean_topic:
        return "Shkruaj nje teme pas ':'"

    plan = [
        f"Lexo teorine kryesore per {clean_topic}.",
        "Shkruaj 3 shembuj te thjeshte.",
        "Provo nje ushtrim ku gabon dhe e rregullon gabimin.",
        "Krijo nje mini-projekt me kete teme.",
        "Ruaj cfare mesove ne notes.json.",
    ]

    note_text = f"Plan mesimi per {clean_topic} u krijua."
    save_note_tool(note_text)

    lines = [f"Plani per: {clean_topic}"]
    for index, step in enumerate(plan, start=1):
        lines.append(f"{index}. {step}")

    return "\n".join(lines)


def progress_message(note_count):
    if note_count == 0:
        return "Fillo me nje hap te vogel."

    if note_count <= 3:
        return "Ke filluar mire."

    if note_count <= 6:
        return "Po nderton rutine te mire."

    return "Shume mire, je duke punuar seriozisht."


def check_progress_tool():
    note_count = len(notes)

    if note_count == 0:
        return "Nuk ke ende shenime. Fillo duke krijuar nje plan mesimi."

    return (
        f"Ke {note_count} shenime te ruajtura.\n"
        f"{progress_message(note_count)}\n"
        "Vazhdo me ushtrime praktike."
    )


def delete_notes_tool():
    answer = input("A je i sigurt? po/jo: ").lower().strip()

    if answer != "po":
        return "Shenimet nuk u fshine."

    notes.clear()
    save_json_file(NOTES_FILE, notes)
    return "Te gjitha shenimet u fshine nga notes.json."


def add_to_history(user_input, response):
    history.append(
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "input": user_input,
            "response": response,
        }
    )
    save_json_file(HISTORY_FILE, history)


def build_response(intent, tool_used, result):
    return {
        "intent": intent,
        "tool_used": tool_used,
        "result": result,
    }


def agent_response(user_input):
    intent = detect_intent(user_input)

    if intent == "exit":
        response = build_response(
            intent,
            None,
            "Duke e mbyllur Study Coach Agent. Suksese ne mesim!",
        )
    elif intent == "help":
        response = build_response(
            intent,
            None,
            (
                "Provo keto komanda:\n"
                "- krijo plan mesimi: Python functions\n"
                "- krijo plan mesimi: AI Agents\n"
                "- kontrollo progresin\n"
                "- ruaj shenim: Sot mesova JSON\n"
                "- shfaq shenimet\n"
                "- fshij shenimet\n"
                "- history\n"
                "- exit"
            ),
        )
    elif intent == "study_plan":
        topic = user_input.split(":", 1)[1]
        response = build_response(
            intent,
            "study_plan_tool",
            study_plan_tool(topic),
        )
    elif intent == "check_progress":
        response = build_response(
            intent,
            "check_progress_tool",
            check_progress_tool(),
        )
    elif intent == "save_note":
        note_text = user_input.split(":", 1)[1]
        response = build_response(
            intent,
            "save_note_tool",
            save_note_tool(note_text),
        )
    elif intent == "show_notes":
        response = build_response(
            intent,
            "show_notes_tool",
            show_notes_tool(),
        )
    elif intent == "delete_notes":
        response = build_response(
            intent,
            "delete_notes_tool",
            delete_notes_tool(),
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
    print("\n--- Study Coach Agent ---")
    print(f"Intent: {response['intent']}")
    print(f"Tool: {response['tool_used']}")
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
    print("Study Coach Agent u nis.")
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
