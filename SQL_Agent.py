import os
from typing import Any

from langchain import hub
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
from langchain_community.utilities import SQLDatabase
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from QueryOutput import QueryOutput
from State import State


def save_graph(graph: CompiledStateGraph):
    image = graph.get_graph().draw_mermaid_png()
    save_path = os.getenv("GRAPH_STATE_SAVE_PATH")

    # Save image to path
    with open(save_path, "wb") as image_file:
        image_file.write(image)

    print("Graph saved to {}".format(save_path))


def try_print_step(step: dict[str, Any]):
    if "__generate_answer" not in step.keys():
        return
    if type(step["__generate_answer"]) is not dict:
        return
    if "answer" not in step["__generate_answer"].keys():
        return

    print(step["__generate_answer"]["answer"].replace("\\n", "\n"))


class SQLAgent:
    def __init__(self):
        self.lang_smith_api_key = os.getenv("LANGSMITH_API_KEY")
        self.lang_smith_tracing = os.getenv("LANGSMITH_TRACING")
        self.db_conn_str = os.getenv("DB_CONNECTION_STRING")
        self.db = SQLDatabase.from_uri(self.db_conn_str)

        self.print_debug_msg = bool(os.getenv("PRINT_DEBUG_MSG"))

        if self.print_debug_msg:
            print(self.db.dialect)
            print(self.db.get_usable_table_names())

            test_query = os.getenv("DB_TEST_QUERY")
            print(test_query)

            self.db.run(test_query)

        model_name = os.getenv("MODEL_NAME")
        prompt_template_name = os.getenv("PROMPT_TEMPLATE_NAME")

        self.llm = ChatOllama(model=model_name)
        self.query_prompt_template = hub.pull(prompt_template_name)

        self.__verify_prompt_template()

    def __verify_prompt_template(self):
        assert len(self.query_prompt_template.messages) == 1
        self.query_prompt_template.messages[0].pretty_print()

    def __write_query(self, state: State):
        """Generate SQL query to fetch information."""
        prompt = self.query_prompt_template.invoke(
            {
                "dialect": self.db.dialect,
                "top_k": 10,
                "table_info": self.db.get_table_info(),
                "input": state["question"],
            }
        )
        structured_llm = self.llm.with_structured_output(QueryOutput)
        result = structured_llm.invoke(prompt)
        return {"query": result["query"]}

    def __execute_query(self, state: State):
        """Execute SQL query."""
        execute_query_tool = QuerySQLDatabaseTool(db=self.db)
        return {"result": execute_query_tool.invoke(state["query"])}

    def __generate_answer(self, state: State):
        """Answer question using retrieved information as context."""
        prompt = (
            "Given the following user question, corresponding SQL query, "
            "and SQL result, answer the user question.\n\n"
            f'Question: {state["question"]}\n'
            f'SQL Query: {state["query"]}\n'
            f'SQL Result: {state["result"]}'
        )
        response = self.llm.invoke(prompt)
        return {"answer": response.content}

    def start(self):
        graph_builder = StateGraph(State).add_sequence(
            [self.__write_query, self.__execute_query, self.__generate_answer]
        )
        graph_builder.add_edge(START, "__write_query")

        memory = MemorySaver()
        graph = graph_builder.compile(checkpointer=memory, interrupt_before=["__execute_query"])

        if self.print_debug_msg:
            save_graph(graph)

        # Now that we're using persistence, we need to specify a thread ID
        # so that we can continue the run after review.
        config = {"configurable": {"thread_id": "1"}}

        while True:
            query = input("What you want to query?: ")

            if self.print_debug_msg:
                stream = graph.stream(
                    {"question": query},
                    config,
                    stream_mode="updates",
                )

                for step in stream:
                    print(step)

            user_approval = input("Do you want to go to execute query? (yes/no): ")

            if user_approval.lower() in ["yes", "y"]:
                # If approved, continue the graph execution
                for step in graph.stream(None, config, stream_mode="updates"):
                    print(step)
                    try_print_step(step)
            else:
                print("Operation cancelled by user.")
                break
