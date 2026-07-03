# Detyre - Study Agent per Nxenesit

## Qellimi

Te ndertohet nje AI Agent i thjeshte ne Python qe mund te:

- njoh llojin e kerkeses se perdoruesit
- perdor disa tools te vegjel
- ruaj historine e kerkesave
- shfaq rezultatet ne menyre te qarte

Kjo detyre bazohet ne logjiken e skedarit `AIagent.py`.

## Kerkesa kryesore

Krijo nje program me emrin:

`study_agent_student.py`

Programi duhet te punoje ne terminal dhe te mbeshtese komandat e meposhtme:

- `pershendetje`
- `llogarit 15 + 7`
- `numero fjalet: Une po mesoj Python`
- `history`
- `exit`

## Pjeset qe duhet t'i implementoni

### 1. Lista `history`

Krijo nje liste bosh me emrin `history` ku do te ruhen kerkesat e perdoruesit.

### 2. Funksioni `detect_intent(user_input)`

Ky funksion duhet te ktheje nje nga keto vlera:

- `exit`
- `greeting`
- `word_count`
- `math`
- `general`

Sugjerim:

- nese user shkruan `exit`, `quit` ose `dal`, kthe `exit`
- nese user shkruan `pershendetje`, `hello` ose `hi`, kthe `greeting`
- nese teksti fillon me `numero fjalet:`, kthe `word_count`
- nese teksti permban `llogarit` ose shenja matematike, kthe `math`
- perndryshe kthe `general`

### 3. Funksioni `calculator_tool(expression)`

Ky funksion duhet:

- te marre nje shprehje matematike
- te kontrolloje nese ka vetem karaktere te lejuara
- te beje llogaritjen
- te ktheje rezultatin ose nje mesazh gabimi

Perdor `try/except`.

### 4. Funksioni `word_count_tool(text)`

Ky funksion duhet te numeroje sa fjale ka nje tekst.

Shembull:

`Une po mesoj AI Agents`

duhet te ktheje:

`5`

### 5. Funksioni `add_to_history(user_input, response)`

Ky funksion duhet te ruaje ne `history`:

- kohen
- input-in e userit
- pergjigjen e agentit

Per timestamp mund te perdoresh:

`datetime.now().strftime("%Y-%m-%d %H:%M:%S")`

### 6. Funksioni `agent_response(user_input)`

Ky funksion eshte pjesa kryesore e agentit.

Detyra e tij eshte:

- te therrase `detect_intent`
- te vendose cfare duhet bere
- te perdore tool-in e duhur
- te krijoje nje pergjigje ne forme dictionary

Forma e pergjigjes duhet te jete e ngjashme me kete:

```python
{
    "intent": "math",
    "tool_used": "calculator_tool",
    "result": 22
}
```

### 7. Funksioni `print_response(response)`

Ky funksion duhet te afishoje ne menyre te rregullt:

- intent-in
- tool-in e perdorur
- rezultatin

### 8. Funksioni `print_history()`

Ky funksion duhet:

- te shfaqe te gjitha kerkesat e ruajtura
- te tregoje timestamp-in
- te tregoje pergjigjen per secilen kerkese

### 9. Funksioni `main()`

Ne `main()` duhet te:

- shfaqen udhezimet fillestare
- merret input nga perdoruesi me `while True`
- nese user shkruan `history`, te thirret `print_history()`
- nese user shkruan komanda tjera, te thirret `agent_response()`
- nese user shkruan `exit`, programi te mbyllet

## Kerkesa minimale

Programi duhet te kete:

- te pakten 5 funksione
- `try/except`
- `history`
- `timestamp`
- perdorim te `if/elif/else`
- nje menu ne terminal

## Bonus

Nese doni me avancu me shume, shtoni edhe njeren nga keto:

- nje intent te ri `date_time` qe tregon daten dhe oren aktuale
- nje intent te ri `reverse_text` qe kthen tekstin mbrapsht
- ruajtjen e `history` ne nje file `.json`
- nje komandë `help` qe shfaq te gjitha komandat e mundshme

## Pyetje teorike

1. Cili eshte roli i `detect_intent()` ne kete program?
2. Pse `calculator_tool()` dhe `word_count_tool()` duhen mbajtur si funksione te ndara?
3. Cfare perfitimi kemi nga ruajtja e `history`?
4. Pse eshte e rendesishme te perdoret `try/except`?
5. Cili eshte dallimi mes `general response` dhe pergjigjes qe vjen nga nje tool?

## Teste qe duhet t'i provoni

Testoni programin me keto input-e:

1. `pershendetje`
2. `llogarit 25 * 16`
3. `numero fjalet: Une po mesoj AI Agents ne Python`
4. `history`
5. `exit`

## Dorezimi

Nxenesi duhet te dorezoje:

- skedarin `study_agent_student.py`
- nje screenshot ose output me disa komanda te testuara

