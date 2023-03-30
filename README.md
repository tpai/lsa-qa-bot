# Labor Standards Act QA Bot

This repository sets up a Telegram bot that can answer questions related to Taiwan's Labor Standards Act.
It uses OpenAI's GPT-3 model for natural language processing and a retrieval-based question answering system.

## Prerequisites

Install the required libraries:

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Build the Docker image
docker build -t lsa-qa-bot .

# Run the Docker image
docker run -e OPENAI_API_KEY=... -e TELEGRAM_TOKEN=... -d lsa-qa-bot:latest
```

## Demo

![](https://i.imgur.com/SUVxSqw.jpg)

![](https://i.imgur.com/TkvxnG6.jpg)
