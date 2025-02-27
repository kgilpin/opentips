import asyncio
import logging
import argparse
import os
from typing import Optional

from opentips.cli.rpc_server import DEFAULT_TIP_DELAY, RPCServer
from opentips.comm.completion import (
    register_completion_handler,
)
from opentips.comm.message_completion import (
    complete as message_complete,
)
from opentips.llm.llm_completion import (
    NoModelFoundError,
    complete as llm_complete,
    get_model,
)
from opentips.tips.diff import diff
from opentips.tips.fetch_tips import fetch_tips_for_diff

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        force=True,
    )
    logging.info(f"Setting up logging at level {level}")


def setup_working_directory(directory: Optional[str]) -> None:
    if not directory:
        return

    if not os.path.exists(directory):
        logger.error(f"Directory {directory} does not exist")
        exit(1)

    os.chdir(directory)


def parse_args():
    parser = argparse.ArgumentParser(
        description="OpenTips - A tool for learning to code via interactive tips",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Increase output verbosity"
    )

    parser.add_argument(
        "-d", "--directory", type=str, default=".", help="Directory to run OpenTips in"
    )

    parser.add_argument(
        "-s",
        "--server",
        action="store_true",
        help="Run persistently as an RPC server",
    )

    parser.add_argument("-p", "--port", type=int, help="Port for RPC server")

    parser.add_argument(
        "--tip_delay",
        type=float,
        default=DEFAULT_TIP_DELAY,
        help="Time in seconds to wait for code edits to stop before starting to discover tips",
    )

    return parser.parse_args()


def enroll_llm_completion():
    register_completion_handler("llm", llm_complete)


def enroll_message_completion():
    register_completion_handler("message", message_complete)


async def main_async():
    args = parse_args()

    setup_logging(args.verbose)
    setup_working_directory(args.directory)

    def is_model_available() -> bool:
        try:
            get_model()
            return True
        except NoModelFoundError:
            return False

    if is_model_available():
        logger.info("Model is available. Using LLM-based completion provider")
        enroll_llm_completion()
    else:
        logger.error("Model is not available. Using message-based completion provider")
        enroll_message_completion()

    run_rpc = args.server or args.port is not None

    async def do_run_rpc():
        port = args.port if args.port is not None else 0
        rpc_server = RPCServer(port=port, tip_delay=args.tip_delay)
        stop_event = asyncio.Event()

        try:
            await rpc_server.start_server()

            logger.info("OpenTips is running! Press Ctrl+C to exit.")

            await stop_event.wait()

        except KeyboardInterrupt:
            logger.info("Shutting down...")
            stop_event.set()
        finally:
            await rpc_server.stop()

    async def do_run_once():
        diff_chunks = diff(new_only=True)
        if not diff_chunks:
            logger.debug("No diff content to analyze")
            return

        tip = await fetch_tips_for_diff(diff_chunks)
        logger.info("Tips:")
        for t in tip.tips:
            print(str(t))

    if run_rpc:
        logger.info("Running in server mode")
        await do_run_rpc()
    else:
        logger.info("Running once")
        await do_run_once()


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
