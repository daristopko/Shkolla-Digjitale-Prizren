# Ky eshte nje shembull i thjeshte i nje AI Agent ne Python, i cili mund te nderroje midis llogaritjeve matematikore dhe leximit te file-ve bazuar ne input-in e perdoruesit.
def detect_intent(user_input):
    text = user_input.lower()

    if "llogarit" in text or "+" in text or "-" in text or "*" in text or "/" in text:
        return "math"

    if "lexo file" in text or "hap file" in text:
        return "file"

    return "general"

# Ky eshte nje shembull i thjeshte i nje tool-i per llogaritje matematikore. Ne nje aplikacion real, do te ishte me e sigurt te perdorje nje library te specializuar per llogaritje, por per qellime demonstrimi, eval eshte i mjaftueshem.
def calculator_tool(expression):
    try:
        return eval(expression)
    except Exception as error:
        return f"Gabim ne llogaritje: {error}"

# Kjo eshte logjika kryesore e agentit, e cila vendos se cfare tool-i te perdore bazuar ne intent-in e zbuluar dhe kthen rezultatin perkatese.
def agent_response(user_input):
    intent = detect_intent(user_input)

    if intent == "math":
        expression = (
            user_input.lower()
            .replace("llogarit", "")
            .strip()
        )
        result = calculator_tool(expression)
        return {
            "intent": intent,
            "tool_used": "calculator_tool",
            "result": result,
        }

    if intent == "file":
        return {
            "intent": intent,
            "tool_used": "file_reader",
            "result": "Ketu me vone mund te shtosh logjiken per lexim te file-it.",
        }

    return {
        "intent": intent,
        "tool_used": None,
        "result": "Kjo kerkese mund te trajtohet me pergjigje normale.",
    }


examples = [
    "Llogarit 25 * 16",
    "Lexo file notes.txt",
    "Cfare eshte nje AI Agent?",
]
# Testimi i agentit me disa input-e shembull
for item in examples:
    print(f"Input: {item}")
    print(agent_response(item))
    print("-" * 40)

