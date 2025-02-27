from typing import Any, Awaitable, Callable, Dict, Optional, TypeVar, Type, Union, cast
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

DEFAULT_TEMPERATURE = 0.0


CompleteCallable = Callable[
    [str, str, float, Optional[Type[T]]], Awaitable[Union[dict, str]]
]

completion_handlers: Dict[str, CompleteCallable[Any]] = {}


def register_completion_handler(name: str, handler: CompleteCallable[T]) -> None:
    completion_handlers[name] = handler


def get_completion_handler(
    handler_name: Optional[str] = None,
) -> CompleteCallable[T]:
    if len(completion_handlers) == 0:
        raise ValueError("No completion handlers")
    elif len(completion_handlers) == 1:
        return next(iter(completion_handlers.values()))

    if not handler_name:
        raise ValueError("No completion handler name provided")

    handler = completion_handlers.get(handler_name)
    if not handler:
        raise ValueError(f"No completion handler found for {handler_name}")

    return handler


def load_completion_response(response: Union[dict, str], response_format: Type[T]) -> T:
    if isinstance(response, str):
        response_str = cast(str, response)
        return response_format.model_validate_json(response_str)

    return response_format.model_validate(response)
