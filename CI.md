## Running the GitHub Actions Locally

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
