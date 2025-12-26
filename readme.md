# LLM-Guided SQL Evidence Extraction

This project implements a lightweight **LLM-assisted pipeline** for discovering and extracting evidentiary artifacts from SQLite databases commonly found in mobile device extractions.

The system separates **discovery** and **extraction** to reduce search space, avoid hallucinated SQL, and preserve explainability.

## Features

- LLM-guided SQL planning with deterministic execution
- Discovery to extraction workflow
- Fixed evidence types: `EMAIL`, `PHONE`, `USERNAME`, `PERSON_NAME`
- Safe SQLite execution with REGEXP support
- UNION / UNION ALL–aware column extraction
- Transparent, inspectable state machine

## Setup

```bash
pip install langchain langgraph python-dotenv
```
