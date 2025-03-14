# Okay, here we go...
import llm
import regex
def prompt_for_evaluation(q:str, a:str):
    system_prompt = f"You are Assistant, you will judge the given parsed answers from the questions.\n\nYour judgement will be written in an explanatory format, highlight both the good and the bad. The judgement must contain:\n1. Measure how relevant the answer from the question asked.\n2. How much it highlights their experience or if it more focused on theories\n3. How 'honest' it sounds or if it actually sound like something overly glorified/made up\nDO NOT make any comment on resume formatting/structure/etc."
    user_prompt = f"User: <parsed_question> {q} </parsed_question>\n<parsed_answer>{a}</parsed_answer> Based on the given data, write down your judgement"
    assist_prompt = "Assistant: Understood, here's my detailed judgement on the answer."
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
        {"role": "assistant", "content": assist_prompt},
    ]

def prompt_for_scoring(com:str):
    system_prompt = f"You are Assistant, you will score the result of a technical test based on a given explanatory result. The score must be formatted between `[ ]` like for example: [Score: 87] the scoring criteria is simply based on the commentary given."
    user_prompt = f"User: <parsed_commentary> {com} </parsed_commentary>\n Write down the score based on the commentary"
    assist_prompt = "Assistant: Understood, here's the score:"
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
        {"role": "assistant", "content": assist_prompt},
    ]

def make_commentary(question, answer):
    q = question
    a = answer
    prompt = prompt_for_evaluation(q,a)
    result = llm.send_prompt(prompt)
    return result

def score_question(commentary_string):
    print(commentary_string)
    com = commentary_string
    prompt = prompt_for_scoring(com)
    result = llm.send_prompt(prompt)
    return result