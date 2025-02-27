# OpenTips

OpenTips provides tips and suggestions for developers right in their code editor. It's like having a helpful colleague who points out potential improvements and best practices as you write code.

## Running the Server and Client

OpenTips provides a JSON RPC server, and also an HTTP endpoint for Server-Sent Events. To run the server, use the following commands:

```bash
export ANTHROPIC_API_KEY=your_api_key
PYTHONPATH=. python -m opentips.cli.main -p 5000 -d ../myproject
```

This command starts the OpenTips server on port 5000, serving tips for the project located in the `../myproject` directory. You can then connect to the server using the OpenTips client program:

```bash
PYTHONPATH=. python -m opentips.cli.client -p 5000 suggest
```

The client provides a variety of commands that allow you to interact with the OpenTips server. For example, you can request a list of available tips, or ask to explain or apply a tip.

## Usage in an IDE Plugin Environment

OpenTips is designed to be used in an IDE plugin environment, such as a Visual Studio Code extension. The server is run automatically as a separate process, and the client can communicate with it over HTTP or via JSON RPC.

In this type of environment, the IDE plugin runs the server with `-p 0`, which allows the OS to assign an available port. This approach is beneficial as it avoids potential port conflicts that might occur if a fixed port number was used. The chosen port is written to the standard output, and the plugin reads this port number. The plugin then connects to the server using the client program, ensuring a smooth and conflict-free setup process.

## Local Development

### Setup

1. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   ```

2. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

### Testing GitHub Actions Locally

You can test the GitHub Actions workflows locally using [act](https://github.com/nektos/act).

1. Install prerequisites:

   ```bash
   # macOS
   brew install act

   # Make sure Docker is running
   ```

2. Create a local environment file:

   ```bash
   echo "GITHUB_TOKEN=test-token" > .env.local
   ```

3. Run the test workflow:

   ```bash
   # Run all platforms (large download, ~12GB)
   act -W .github/workflows/test.yml --env-file .env.local

   # Run single platform (faster)
   act -W .github/workflows/test.yml -j test --env-file .env.local --platform ubuntu-latest
   ```

Note: Windows builds cannot be tested locally due to runner limitations.
