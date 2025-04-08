# RAG DEMO

![GitHub](https://img.shields.io/github/license/laolarou726/Text_2_SQL_Demo?logo=github&style=for-the-badge)
![Maintenance](https://img.shields.io/maintenance/yes/2025?logo=diaspora&style=for-the-badge)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/laolarou726/Text_2_SQL_Demo?style=for-the-badge)
![GitHub closed pull requests](https://img.shields.io/github/issues-pr-closed/laolarou726/Text_2_SQL_Demo?logo=github&style=for-the-badge)
![GitHub repo size](https://img.shields.io/github/repo-size/laolarou726/Text_2_SQL_Demo?logo=github&style=for-the-badge)

This is a minimal demo project to show the capabilities of a Text2SQL system using `LangChain`, it contains all the things you required to build a basic RAG system. Using Chinook as the sample database.

## Before Start

First, make a copy of `.env.sample` and rename it to `.env`, and change any fields that need to be changed

Then:

1. Download `Chinook Database` from [here](https://database.guide/2-sample-databases-sqlite/).
   1. Change the connection string in the `.env` file.
2. Setup the `Ollama` for the document tokenization and interaction
   1. See [Setup - OllamaEmbeddings](https://python.langchain.com/docs/integrations/text_embedding/ollama/)
   2. See [Ollama](https://ollama.com/)
3. Get your LangSmith API Key from [here](https://smith.langchain.com/hub).

## Start the demo

Run `python main.py` and type anything you want to ask the RAG system

## Screenshots

![image](https://github.com/user-attachments/assets/73a21efa-5502-465a-b890-16f4523b1504)
