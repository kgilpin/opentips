## RPC

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

- [ ] Remove language model info from the "service" walkthrough
- [ ] When the user manually refreshes the tips, show a progress indicator message or in the status bar.
- [ ] Provide status bar feedback when the server is running.
- [x] Rely on the server to filter tips for code applicability.
- [x] Apply a Decoration to the lines that are changed by the "Apply" feature.
- [x] Clean up the encoding / decoding of tip ids and remove when possible.
- [x] Improve context matching to consider multiple lines of context.
- [x] Hunt for the tip "context" in the code file. Make minor changes to the tip positioning, but if the context is no longer
      present, hide or even dismiss the tip.
- [x] Show the number of available tips in the Activity bar (and in the status bar?). This will give the user a sense of how many
      tips are available, and give them a way to navigate to the tip list.

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
