import asyncio
import argparse
import logging
from colorama import Fore, init as colorama_init
from difflib import unified_diff

from opentips.cli.main import setup_logging
from opentips.cli.rpc_client import RPCClient, RPCError
from opentips.tips.rpc_types import PatchResponse, Tip, TipList

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description="OpenTips CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Increase output verbosity"
    )

    parser.add_argument(
        "-p", "--port", type=int, help="Port to connect to the RPC server", default=5000
    )

    parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        help="Timeout for waiting for response",
        default=30,
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Echo command
    echo_parser = subparsers.add_parser("echo", help="Send echo message")
    echo_parser.add_argument("message", help="Message to echo")

    # Changed command
    changed_parser = subparsers.add_parser("changed", help="Notify about changed files")
    changed_parser.add_argument(
        "--immediate", help="Queue the job immediately", action="store_true"
    )
    changed_parser.add_argument("files", nargs="+", help="List of changed files")

    # Suggest command
    suggest_parser = subparsers.add_parser(
        "suggest", help="Suggest tips on changed files"
    )
    suggest_parser.add_argument(
        "--new_only", help="Only suggest tips on new diffs", action="store_true"
    )

    # List available tips
    list_parser = subparsers.add_parser("list", help="List all available tips")
    list_parser.add_argument(
        "--limit", type=int, help="Limit the number of tips to list"
    )

    # Explain tip command
    explain_parser = subparsers.add_parser("explain", help="Explain a tip")
    explain_parser.add_argument("tip_id", type=str, help="Tip id")

    # Apply tip command
    apply_parser = subparsers.add_parser("apply", help="Apply a tip")
    apply_parser.add_argument("tip_id", type=str, help="Tip id")

    # Build patch command
    build_patch_parser = subparsers.add_parser(
        "build_patch", help="Build a patch for a tip"
    )
    build_patch_parser.add_argument("tip_id", type=str, help="Tip id")

    return parser.parse_args()


async def main_async():
    colorama_init()

    args = parse_args()
    setup_logging(args.verbose)
    timeout = args.timeout

    async def wait_for_event(event):
        try:
            await asyncio.wait_for(event.wait(), timeout)
        except asyncio.TimeoutError:
            logger.warning(f"Timed out waiting for {event}")

    client = RPCClient(port=args.port)
    try:
        await client.connect()

        if args.command == "echo":
            echo_received = asyncio.Event()

            @client.on_event("echo")
            async def handle_echo(data):
                logger.info(f"Received echo: {data}")
                echo_received.set()

            result = await client.call("echo", message=args.message)
            logger.info(f"Echo response: {result}")

            await wait_for_event(echo_received)

        elif args.command == "changed":
            tips_received = asyncio.Event()

            @client.on_event("tips")
            async def handle_tips(data):
                logger.info("Received tips:")
                tips_data = data.get("tips", [])
                for tip_data in tips_data:
                    tip = Tip.model_validate(tip_data)
                    print(tip.format_as_line())
                tips_received.set()

            changed_params = {"file_names": args.files}
            if args.immediate:
                changed_params["immediate"] = True
            result = await client.call("changed", **changed_params)
            logger.info(f"Changed response: {result}")

            if result["file_names"]:
                await wait_for_event(tips_received)

        elif args.command == "suggest":
            params = {}
            if args.new_only is not None:
                params["new_only"] = args.new_only
            else:
                params["new_only"] = False

            tips_data = await client.call("suggest", **params)
            tips = TipList.model_validate(tips_data)
            logger.info("Suggested tips:")
            for tip in tips.tips:
                print(tip.format_as_line())

        elif args.command == "list":
            tips_data = await client.call("list_tips", limit=args.limit)
            tips = [Tip.model_validate(tip_data) for tip_data in tips_data]
            logger.info("Available tips:")
            for tip in tips:
                print(tip.format_as_line())

        elif args.command == "explain":
            result = await client.call("explain_tip", tip_id=args.tip_id)
            print(result["explanation"])

        elif args.command == "apply":
            result = await client.call("apply_tip", tip_id=args.tip_id)
            patch_response = PatchResponse.model_validate(result)

            if not patch_response.success:
                print("No patches generated")

            def generate_diff(search: str, replace: str, filename: str) -> str:
                """Generate a unified diff between search and replace strings"""
                search_lines = search.splitlines(keepends=True)
                replace_lines = replace.splitlines(keepends=True)
                return "".join(
                    unified_diff(
                        search_lines,
                        replace_lines,
                        fromfile=f"a/{filename}",
                        tofile=f"b/{filename}",
                    )
                )

            def colorize_diff(diff: str) -> str:
                """Add ANSI colors to diff output"""
                colored = []
                for line in diff.splitlines():
                    if line.startswith("-"):
                        colored.append(f"{Fore.RED}{line}{Fore.RESET}")
                    elif line.startswith("+"):
                        colored.append(f"{Fore.GREEN}{line}{Fore.RESET}")
                    elif line.startswith("@"):
                        colored.append(f"{Fore.CYAN}{line}{Fore.RESET}")
                    else:
                        colored.append(line)
                return "\n".join(colored)

            for patch in patch_response.patches:
                diff = generate_diff(patch.search, patch.replace, patch.file_name)
                print(colorize_diff(diff))
                print()

        else:
            logger.error("No command specified")

    except (ValueError, RPCError) as e:
        print(str(e))
        exit(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await client.disconnect()


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
