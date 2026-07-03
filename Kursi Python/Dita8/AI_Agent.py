from datetime import datetime


history = []


def detect_intent(user_input):
    text = user_input.lower().strip()

    if text in {"exit", "quit", "dal", "mbyll", "ndal", "stop"}:
        return "exit"

    if "pershendetje" in text or "hello" in text or "hi" in text:
        return "greeting"

    if text.startswith("numero fjalet:"):
        return "word_count"

    if "llogarit" in text or any(symbol in text for symbol in ["+", "-", "*", "/", "(", ")", "."]):
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


def word_count_tool(text):
    words = text.split()
    return len(words)


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
            "result": "Duke e mbyllur Study Agent. Suksese ne mesim!",
        }
        add_to_history(user_input, response)
        return response

    if intent == "greeting":
        response = {
            "intent": intent,
            "tool_used": None,
            "result": "Pershendetje! Une jam Study Agent. Mund te bej llogaritje dhe numerim fjalesh.",
        }
        add_to_history(user_input, response)
        return response

    if intent == "word_count":
        text = user_input.split(":", 1)[1].strip()
        result = word_count_tool(text)
        response = {
            "intent": intent,
            "tool_used": "word_count_tool",
            "result": f"Teksti ka {result} fjale.",
        }
        add_to_history(user_input, response)
        return response

    if intent == "math":
        expression = user_input.lower().replace("llogarit", "").strip()
        result = calculator_tool(expression)
        response = {
            "intent": intent,
            "tool_used": "calculator_tool",
            "result": result,
        }
        add_to_history(user_input, response)
        return response

    response = {
        "intent": intent,
        "tool_used": None,
        "result": "Mund te me kerkosh pershendetje, llogaritje, ose numerim fjalesh.",
    }
    add_to_history(user_input, response)
    return response


def print_response(response):
    print("\n--- Pergjigjja e Agentit ---")
    print(f"Intent: {response['intent']}")
    print(f"Tool: {response['tool_used']}")
    print(f"Rezultati: {response['result']}")
    print("-" * 30)


def print_history():
    print("\n--- History ---")
    if not history:
        print("Nuk ka ende kerkesa te ruajtura.")
        return

    for index, item in enumerate(history, start=1):
        print(f"{index}. [{item['timestamp']}] {item['input']}")
        print(f"   {item['response']['result']}")


def main():
    print("Study Agent u nis.")
    print("Komanda qe mund te provosh:")
    print("- pershendetje")
    print("- llogarit 25 * 16")
    print("- numero fjalet: Une po mesoj AI Agents")
    print("- history")
    print("- exit")

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
