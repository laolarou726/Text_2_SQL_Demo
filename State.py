from typing_extensions import TypedDict


class State(TypedDict):
    question: str
    query: str
    result: str
    answer: str
