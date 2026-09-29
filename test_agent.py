import os

from dotenv import load_dotenv

from agent import ask_agent


load_dotenv()


while True:

    question = input("\nYou: ")

    if question.lower() == "exit":
        break

    answer = ask_agent(
        question
    )

    print(
        "\nAI:",
        answer
    )
