from typing import Callable, TYPE_CHECKING, Union, Coroutine, Any, TypeVar

if TYPE_CHECKING:
    from .. import Cog, ApplicationContext

T = TypeVar('T')

Coro = Coroutine[Any, Any, T]
MaybeCoro = Union[T, Coro[T]]
CoroFunc = Callable[..., Coro[Any]]

Check = Union[Callable[["Cog", "ApplicationContext[Any]"], MaybeCoro[bool]],
              Callable[["ApplicationContext[Any]"], MaybeCoro[bool]]]
Hook = Union[Callable[["Cog", "ApplicationContext[Any]"], Coro[Any]], Callable[["ApplicationContext[Any]"], Coro[Any]]]
Error = Union[Callable[["Cog", "ApplicationContext[Any]", "CommandError"], Coro[Any]],
              Callable[["ApplicationContext[Any]", "CommandError"], Coro[Any]]]
