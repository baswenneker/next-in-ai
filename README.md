# Write a newsletter in 5 minutes with GPT
Hi, my name is [Bas](https://www.linkedin.com/in/baswenneker/) and I'm the author of the Dutch AI newsletter [Next in AI](https://nextinai.beehiiv.com/). I've written this Python script to automate 80% of the process of writing a newsletter. It's not perfect, I always rewrite the output. But it saves me a lot of time. I hope it can help you too.

## Requirements
- Visual Studio Code ([DevContainer](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers))
- OpenAI API key
- Docker

## Quickstart
1. Get an OpenAI [API Key](https://platform.openai.com/account/api-keys).
2. Add the API key and Pocket RSS feed url to the .env file (see .env.example).
3. Download the [latest release](https://github.com/baswenneker/next-in-ai).
4. Install the Remote - Containers extension in VS Code.
5. Open command palette with F1 and type Dev Containers: Open Folder in Container.
6. Open a terminal and run `python main.py`.