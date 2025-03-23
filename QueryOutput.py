from typing_extensions import Annotated
from typing_extensions import TypedDict


class QueryOutput(TypedDict):
    """Generated SQL query."""

    query: Annotated[str, ..., "Syntactically valid SQL query."]
