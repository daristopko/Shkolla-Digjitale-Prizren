from datetime import datetime

history = []
notes = []

def detect_intent(user_input):
    text = user_input.lower().strip()

    if text in {"exit", "quit", "dal", "mbyll", "shko", "largohu", "bye", "goodbye", "see you", "mshele", "mbylle"}:
        return "exit"

    if text in {"help", "ndihme"}:
        return "help"

    if text.startswith("ruaj shenim:"):
        return "save_note"

    if text == "shfaq shenimet":
        return "show_notes"

    if text.startswith("numero fjalet:"):
        return "word_count"

    if "llogarit" in text or any(symbol in text for symbol in ["+", "-", "*", "/","**"]):
        return "math"

    if "sa eshte ora" in text or "ora" == text:
        return "time"

    return "general"


def calculator_tool(expression):
    allowed_chars = "0123456789+-*/(). **"

    if not all(char in allowed_chars for char in expression):
        return "Shprehja permban karaktere qe nuk lejohen."

    try:
        return eval(expression, {"__builtins__": {}}, {})
    except Exception as error:
        return f"Gabim ne llogaritje: {error}"


def word_count_tool(text):
    return len(text.split())


def time_tool():
    return datetime.now().strftime("%H:%M:%S")


def save_note_tool(note_text):
    clean_note = note_text.strip()

    if not clean_note:
        return "Shenimi eshte bosh. Shkruaj dicka pas ':'."

    notes.append(
        {
            "text": clean_note,
            "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    )
    return f"Shenimi u ruajt: {clean_note}"


def show_notes_tool():
    if not notes:
        return "Nuk ka ende shenime te ruajtura."

    lines = []
    for index, note in enumerate(notes, start=1):
        lines.append(f"{index}. {note['text']} ({note['saved_at']})")
    return "\n".join(lines)


def add_to_history(user_input, response):
    history.append(
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "input": user_input,
            "response": response,
        }
    )


def agent_response(user_input):
    intent = detect_intent(user_input)

    if intent == "exit":
        response = {
            "intent": intent,
            "tool_used": None,
            "result": "Duke e mbyllur Memory Agent. Suksese!",
        }
    elif intent == "help":
        response = {
            "intent": intent,
            "tool_used": None,
            "result": (
                "Provo keto komanda:\n"
                "- llogarit 45 / 5\n"
                "- numero fjalet: Une po mesoj AI Agents\n"
                "- ruaj shenim: Duhet te praktikoj Python\n"
                "- shfaq shenimet\n"
                "- sa eshte ora\n"
                "- history\n"
                "- exit"
            ),
        }
    elif intent == "save_note":
        note_text = user_input.split(":", 1)[1]
        response = {
            "intent": intent,
            "tool_used": "save_note_tool",
            "result": save_note_tool(note_text),
        }
    elif intent == "show_notes":
        response = {
            "intent": intent,
            "tool_used": "show_notes_tool",
            "result": show_notes_tool(),
        }
    elif intent == "word_count":
        text = user_input.split(":", 1)[1].strip()
        response = {
            "intent": intent,
            "tool_used": "word_count_tool",
            "result": f"Teksti ka {word_count_tool(text)} fjale.",
        }
    elif intent == "math":
        expression = user_input.lower().replace("llogarit", "").strip()
        response = {
            "intent": intent,
            "tool_used": "calculator_tool",
            "result": calculator_tool(expression),
        }
    elif intent == "time":
        response = {
            "intent": intent,
            "tool_used": "time_tool",
            "result": f"Ora aktuale eshte {time_tool()}",
        }
    else:
        response = {
            "intent": intent,
            "tool_used": None,
            "result": "Nuk e kuptova kerkesen. Shkruaj 'help' per komandat.",
        }

    add_to_history(user_input, response)
    return response


def print_response(response):
    print("\n--- Pergjigjja e Agentit ---")
    print(f"Intent: {response['intent']}")
    print(f"Tool: {response['tool_used']}")
    print(f"Rezultati:\n{response['result']}")
    print("-" * 30)


def print_history():
    print("\n--- History ---")
    if not history:
        print("Nuk ka ende histori.")
        return

    for index, item in enumerate(history, start=1):
        print(f"{index}. [{item['timestamp']}] {item['input']}")
        print(f"   {item['response']['result']}")


def main():
    print("Memory Agent u nis.")
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
