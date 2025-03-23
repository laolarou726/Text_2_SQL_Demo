from dotenv import load_dotenv

from SQL_Agent import SQLAgent

if __name__ == '__main__':
    load_dotenv(override=True)

    sql_agent = SQLAgent()
    sql_agent.start()
