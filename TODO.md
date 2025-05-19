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

## VSCode

- [ ] Auto-update the opentips package when a new version is available.
- [ ] (bug) "OpenTips - Open Service Installation Walkthrough" opens the generic list of VSCode walkthroughs.
- [ ] When the user manually refreshes the tips, show a progress indicator message.
- [ ] Figure out how to embed commands as Buttons in the walkthrough pages.
- [ ] Deprecate this by installing Python automatically:
  > Once you've selected the Python interpreter, run the command Python: Create Terminal from the Command Palette (Ctrl+Shift+P) or (Cmd+Shift+P) to open a terminal with the selected Python interpreter:
- [ ] Show Markdown Preview of each tip rather than a text document?
- [ ] Backend accepts delete_after_apply parameter in apply_tip. Frontend doesn't pass this parameter.
- [ ] Add event types. Example:

```typescript
interface TipDeletedEvent {
  type: "tip_deleted";
  data: {
    tip_id: string;
    reason: string;
  };
}
```

- [x] Update the tip list image on the marketplace page
- [x] Provide status feedback on the service operational status
- [x] Implement the priority field
- [x] Don't run tip server when a fixed port is configured.
- [x] Show status webview in the sidebar panel.
- [x] Show a gear icon in the Panel to open the settings.
- [x] Update help to include a link to open the Output channel
  > [Open Output Channel](command:workbench.action.output.toggleOutput)
- [x] Provide the Marketplace listing page.
- [x] Remove language model info from the "service" walkthrough
- [x] Rely on the server to filter tips for code applicability.
- [x] Apply a Decoration to the lines that are changed by the "Apply" feature.
- [x] Clean up the encoding / decoding of tip ids and remove when possible.
- [x] Improve context matching to consider multiple lines of context.
- [x] Hunt for the tip "context" in the code file. Make minor changes to the tip positioning, but if the context is no longer
      present, hide or even dismiss the tip.
- [x] Show the number of available tips in the Activity bar (and in the status bar?). This will give the user a sense of how many
      tips are available, and give them a way to navigate to the tip list.

## Windows

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

## Use TypeScript event types

Use TypeScript event types for the listener parameter to improve type safety and code clarity in the `OpenTipsSSEClient` class.

In TypeScript, you can define specific event types for your custom events. This practice enhances type checking and provides better autocompletion in your IDE. Here's how you could implement this suggestion:

1. Define an interface for your custom events:

```typescript
interface OpenTipsEvents {
  tips: (data: TipList) => void;
  // Add other event types as needed
}
```

2. Use this interface when creating the EventEmitter:

```typescript
class OpenTipsSSEClient extends EventEmitter<OpenTipsEvents> {
  // ...
}
```

3. Update the constructor to use the typed listener:

```typescript
constructor(port: number, listener: <K extends keyof OpenTipsEvents>(type: K, data: Parameters<OpenTipsEvents[K]>[0]) => void) {
  // ...
}
```

4. Use the typed emit method:

```typescript
this.emit("tips", eventData as TipList);
```

By implementing these changes, you'll get better type checking for event names and their corresponding data types. This will help catch potential errors at compile-time and provide better code completion in your IDE.

The benefits of this approach include:

1. Improved type safety: TypeScript will ensure you're using correct event names and data types.
2. Better code clarity: The event types are explicitly defined, making it easier to understand what events are available and what data they provide.
3. Enhanced developer experience: IDEs can provide better autocompletion and type inference when working with events.

This refactoring is considered low complexity because it mainly involves adding type definitions and doesn't require significant changes to the existing logic.
