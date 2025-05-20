## RPC

- [ ] Normalize across tips to eliminate duplicates
- [ ] Don't re-analyze unchanged chunks of code
- [x] Implement "priority" handling in the IDE extension.
- [x] Use dash-case for tips
- [x] Document the 'complete' event and 'complete_response' RPC method
- [x] Document RPC methods and responses.
- [x] Make aider a runtime dependency only.
- [x] Package the opentips server as a standalone executable.
- [x] Prioritize and prune the tips list after generating new tips, to keep the overall tips list manageable.
- [x] When handling list_tips, check that all tips are valid before returning them.
- [x] Verify on the server side that existing tips are applicable to the code context, when the code changes.
- [x] Replace SSE with polling over JSON-RPC, to enable the extension to work in environments where SSE is not available.
- [x] Don't compute tips for diff chunks that have been observed before.
- [x] Emit "apply_tip" and "delete_tip" events
- [x] Associate each tip to some code context (e.g. the contents of a line). Hide the tip when the context is not visible / available
      any more. This will cut down on the display of "stale" tips that apply to out-of-date code.

## Windows

TIP: The ENOENT error indicates cmd.exe cannot be found. Use process.env.COMSPEC or process.env.SystemRoot to reliably locate cmd.exe on Windows systems.

[khhoah] Executing command: cmd.exe /c "c:\Users\kgilpin\.vscode\extensions\opentips.opentips-1.0.0\scripts\install_win.bat"
[khhoah] spawn C:\WINDOWS\system32\cmd.exe ENOENT

Ignore .venv and venv in the file watcher by default

## Code signing

For Windows:

```
WIN_SIGNING_CERT: Base64 encoded .pfx certificate
WIN_SIGNING_CERT_PASSWORD: Certificate password
```

For MacOS:

```
MACOS_CERTIFICATE: Base64 encoded .p12 certificate
MACOS_CERTIFICATE_PWD: Certificate password
KEYCHAIN_PASSWORD: Any secure password for the temporary keychain
MACOS_IDENTITY: Your signing identity (e.g., "Developer ID Application: Your Name (TEAM_ID)")
```

> **Important**: These sensitive credentials should never be stored directly in your repository. Store them securely as:
>
> - GitHub repository secrets if using GitHub Actions
> - Environment variables in your CI/CD pipeline
> - A secure secrets management system (e.g., HashiCorp Vault, AWS Secrets Manager)
>
> For local development, consider using a tool like `dotenv` with a `.env` file that is excluded from version control via `.gitignore`.
