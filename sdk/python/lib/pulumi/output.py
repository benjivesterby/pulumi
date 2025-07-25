# Copyright 2016-2025, Pulumi Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import asyncio
import contextlib
import json
import os
from functools import reduce
from inspect import isawaitable
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Dict,
    Generic,
    List,
    Mapping,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)

from . import log
from . import _types
from .runtime import rpc
from .runtime.sync_await import _sync_await
from .runtime.settings import SETTINGS
from .runtime._serialization import (
    _serialization_enabled,
    _secrets_allowed,
    _set_contained_secrets,
)

if TYPE_CHECKING:
    from .resource import Resource

T = TypeVar("T")
T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
T_co = TypeVar("T_co", covariant=True)
U = TypeVar("U")

Input = Union[T, Awaitable[T], "Output[T]"]
Inputs = Mapping[str, Input[Any]]
InputType = Union[T, Mapping[str, Any]]


class Output(Generic[T_co]):
    """
    Output helps encode the relationship between Resources in a Pulumi application. Specifically an
    Output holds onto a piece of Data and the Resource it was generated from. An Output value can
    then be provided when constructing new Resources, allowing that new Resource to know both the
    value as well as the Resource the value came from.  This allows for a precise 'Resource
    dependency graph' to be created, which properly tracks the relationship between resources.
    """

    _is_known: Awaitable[bool]
    """
    Whether or not this 'Output' should actually perform .apply calls.  During a preview,
    an Output value may not be known (because it would have to actually be computed by doing an
    'update').  In that case, we don't want to perform any .apply calls as the callbacks
    may not expect an undefined value.  So, instead, we just transition to another Output
    value that itself knows it should not perform .apply calls.
    """

    _is_secret: Awaitable[bool]
    """
    Whether or not this 'Output' should be treated as containing secret data. Secret outputs are tagged when
    flowing across the RPC interface to the resource monitor, such that when they are persisted to disk in
    our state file, they are encrypted instead of being in plaintext.
    """

    _future: Awaitable[T_co]
    """
    Future that actually produces the concrete value of this output.
    """

    _resources: Awaitable[Set["Resource"]]
    """
    The list of resources that this output value depends on.
    """

    def __init__(
        self,
        resources: Union[Awaitable[Set["Resource"]], Set["Resource"]],
        future: Awaitable[T_co],
        is_known: Awaitable[bool],
        is_secret: Optional[Awaitable[bool]] = None,
    ) -> None:
        is_known = asyncio.ensure_future(is_known)
        future = asyncio.ensure_future(future)
        # keep track of all created outputs so we can check they resolve
        with SETTINGS.lock:
            SETTINGS.outputs.append(future)

        def cleanup(fut: "asyncio.Future[T_co]") -> None:
            if fut.cancelled() or (fut.exception() is not None):
                # if cancelled or error'd leave it in the deque to pick up at program exit
                return
            # else remove it from the deque
            with SETTINGS.lock:
                try:
                    SETTINGS.outputs.remove(fut)
                except ValueError:
                    # if it's not in the deque then it's already been removed in wait_for_rpcs
                    pass

        future.add_done_callback(cleanup)

        async def is_value_known() -> bool:
            return await is_known and not contains_unknowns(await future)

        if isinstance(resources, set):
            self._resources = asyncio.Future()
            self._resources.set_result(resources)
        else:
            self._resources = asyncio.ensure_future(resources)

        self._future = future
        self._is_known = asyncio.ensure_future(is_value_known())

        if is_secret is not None:
            self._is_secret = asyncio.ensure_future(is_secret)
        else:
            self._is_secret = asyncio.Future()
            self._is_secret.set_result(False)

    # Private implementation details - do not document.
    def resources(self) -> Awaitable[Set["Resource"]]:
        return self._resources

    def future(self, with_unknowns: Optional[bool] = None) -> Awaitable[Optional[T_co]]:
        # If the caller did not explicitly ask to see unknown values and the value of this output contains unnkowns,
        # return None. This preserves compatibility with earlier versios of the Pulumi SDK.
        async def get_value() -> Optional[T_co]:
            val = await self._future
            return None if not with_unknowns and contains_unknowns(val) else val

        return asyncio.ensure_future(get_value())

    def is_known(self) -> Awaitable[bool]:
        return self._is_known

    # End private implementation details.

    def __getstate__(self):
        """
        Serialize this Output into a dictionary for pickling, only when serialization is enabled.
        """

        if not _serialization_enabled():
            raise Exception("__getstate__ can only be called during serialization")

        value, is_secret = _sync_await(asyncio.gather(self.future(), self.is_secret()))

        if is_secret:
            if _secrets_allowed():
                _set_contained_secrets(True)
            else:
                raise Exception("Secret outputs cannot be captured")

        return {"value": value}

    def __setstate__(self, state):
        """
        Deserialize this Output from a dictionary, only when serialization is enabled.
        """

        if not _serialization_enabled():
            raise Exception("__setstate__ can only be called during deserialization")

        value = state["value"]

        # Replace '.get' with a function that returns the value without raising an error.
        self.get = lambda: value

        def error(name: str):
            def f(*args: Any, **kwargs: Any):
                raise Exception(
                    f"'{name}' is not allowed from inside a cloud-callback. "
                    + "Use 'get' to retrieve the value of this Output directly."
                )

            return f

        # Replace '.apply' and other methods on Output with implementations that raise an error.
        self.apply = error("apply")
        self.resources = error("resources")
        self.future = error("future")
        self.is_known = error("is_known")
        self.is_secret = error("is_secret")

    def get(self) -> T_co:
        """
        Retrieves the underlying value of this Output.

        This function is only callable in code that runs post-deployment. At this point all Output
        values will be known and can be safely retrieved. During pulumi deployment or preview
        execution this must not be called (and will raise an error). This is because doing so would
        allow Output values to flow into Resources while losing the data that would allow the
        dependency graph to be changed.
        """
        raise Exception(
            "Cannot call '.get' during update or preview. To manipulate the value of this Output, "
            + "use '.apply' instead."
        )

    def is_secret(self) -> Awaitable[bool]:
        return self._is_secret

    def apply(
        self, func: Callable[[T_co], Input[U]], run_with_unknowns: bool = False
    ) -> "Output[U]":
        """
        Transforms the data of the output with the provided func.  The result remains an
        Output so that dependent resources can be properly tracked.

        'func' should not be used to create resources unless necessary as 'func' may not be run during some program executions.

        'func' can return other Outputs.  This can be handy if you have a Output<SomeVal>
        and you want to get a transitive dependency of it.

        This function will be called during execution of a `pulumi up` or `pulumi preview` request.
        It may not run when the values of the resource is unknown.

        :param Callable[[T_co],Input[U]] func: A function that will, given this Output's value, transform the value to
               an Input of some kind, where an Input is either a prompt value, a Future, or another Output of the given
               type.
        :return: A transformed Output obtained from running the transformation function on this Output's value.
        :rtype: Output[U]
        """
        result_resources: asyncio.Future[Set["Resource"]] = asyncio.Future()
        result_is_known: asyncio.Future[bool] = asyncio.Future()
        result_is_secret: asyncio.Future[bool] = asyncio.Future()

        # The "run" coroutine actually runs the apply.
        async def run() -> U:
            resources: Set["Resource"] = set()
            try:
                # Await this output's details.
                resources = await self._resources
                is_known = await self._is_known
                is_secret = await self._is_secret
                value = await self._future

                # Only perform the apply if the engine was able to give us an actual value for this
                # Output or if the caller is able to tolerate unknown values.
                do_apply = is_known or run_with_unknowns
                if not do_apply:
                    # We didn't actually run the function, our new Output is definitely
                    # **not** known.
                    result_resources.set_result(resources)
                    result_is_known.set_result(False)
                    result_is_secret.set_result(is_secret)
                    return cast(U, None)

                # If we are running with unknown values and the value is explicitly unknown but does not actually
                # contain any unknown values, collapse its value to the unknown value. This ensures that callbacks
                # that expect to see unknowns during preview in outputs that are not known will always do so.
                if not is_known and run_with_unknowns and not contains_unknowns(value):
                    value = cast(T_co, UNKNOWN)

                transformed: Input[U] = func(value)
                # Transformed is an Input, meaning there are three cases:
                #  1. transformed is an Output[U]
                if isinstance(transformed, Output):
                    transformed_as_output = cast(Output[U], transformed)
                    # Forward along the inner output's _resources, _is_known and _is_secret values.
                    transformed_resources = await transformed_as_output._resources
                    result_resources.set_result(resources | transformed_resources)
                    result_is_known.set_result(await transformed_as_output._is_known)
                    result_is_secret.set_result(
                        await transformed_as_output._is_secret or is_secret
                    )
                    result = await transformed_as_output.future(with_unknowns=True)
                    # future shouldn't return None because we passed with_unknowns=True, but we can't RTTI check that
                    # because the U value itself might be None.
                    return cast(U, result)

                #  2. transformed is an Awaitable[U]
                if isawaitable(transformed):
                    # Since transformed is not an Output, it is known.
                    result_resources.set_result(resources)
                    result_is_known.set_result(True)
                    result_is_secret.set_result(is_secret)
                    return await cast(Awaitable[U], transformed)

                #  3. transformed is U. It is trivially known.
                result_resources.set_result(resources)
                result_is_known.set_result(True)
                result_is_secret.set_result(is_secret)
                return cast(U, transformed)
            finally:
                with contextlib.suppress(asyncio.InvalidStateError):
                    result_resources.set_result(resources)

                with contextlib.suppress(asyncio.InvalidStateError):
                    result_is_known.set_result(False)

                with contextlib.suppress(asyncio.InvalidStateError):
                    result_is_secret.set_result(False)

        run_fut = asyncio.ensure_future(run())
        return Output(result_resources, run_fut, result_is_known, result_is_secret)

    def __getattr__(self, item: str) -> "Output[Any]":  # type: ignore
        """
        Syntactic sugar for retrieving attributes off of outputs.

        Note that strictly speaking, this implementation of __getattr__ violates
        the contract expected by Python. __getattr__ is expected to raise
        (synchronously) an AttributeError if the attribute is not found.
        However, we return an Output value, which is asynchronous and represents
        a future value. If we try to lift an attribute that does not exist
        therefore, we'll violate the contract by returning an Output that will
        later blow up with an AttributeError. This means that builtins such as
        hasattr generally won't work correctly on Outputs.

        This is generally fine for most Pulumi use cases, but it can cause
        problems when interacting with other libraries that expect attribute
        access to behave correctly. To try and strike a balance that works in a
        majority of cases, we raise an AttributeError immediately if the
        attribute is one of a set that we expect not to need to lift in order to
        make provider SDKs ergonomic (e.g., things that "look reserved" such as
        class-private identifiers and dunder methods).

        :param str item: An attribute name.
        :return: An Output of this Output's underlying value's property with the given name.
        :rtype: Output[Any]
        """
        if item.startswith("__"):
            raise AttributeError(f"'Output' object has no attribute '{item}'")

        def lift(v: Any) -> Any:
            return UNKNOWN if isinstance(v, Unknown) else getattr(v, item)

        return self.apply(lift, True)

    def __getitem__(self, key: Any) -> "Output[Any]":
        """
        Syntactic sugar for looking up attributes dynamically off of outputs.

        :param Any key: Key for the attribute dictionary.
        :return: An Output of this Output's underlying value, keyed with the given key as if it were a dictionary.
        :rtype: Output[Any]
        """

        def lift(v: Any) -> Any:
            return UNKNOWN if isinstance(v, Unknown) else cast(Any, v)[key]

        return self.apply(lift, True)

    def __iter__(self) -> Any:
        """
        Output instances are not iterable, but since they implement __getitem__ we need to explicitly prevent
        iteration by implementing __iter__ to raise a TypeError.
        """
        raise TypeError(
            "'Output' object is not iterable, consider iterating the underlying value inside an 'apply'"
        )

    @overload
    @staticmethod
    def from_input(val: "Output[U]") -> "Output[U]": ...

    @overload
    @staticmethod
    def from_input(val: Input[U]) -> "Output[U]": ...

    @staticmethod
    def from_input(val: Input[U]) -> "Output[U]":
        """
        Takes an Input value and produces an Output value from it, deeply unwrapping nested Input values through nested
        lists, dicts, and input classes.  Nested objects of other types (including Resources) are not deeply unwrapped.

        :param Input[U] val: An Input to be converted to an Output.
        :return: A deeply-unwrapped Output that is guaranteed to not contain any Input values.
        :rtype: Output[U]
        """

        # Is it an output already? Recurse into the value contained within it.
        if isinstance(val, Output):
            return val.apply(Output.from_input, True)

        # Is it an input type (i.e. args class)? Recurse into the values within.
        typ = type(val)
        if _types.is_input_type(typ):
            # We know that any input type can safely be decomposed into it's `__dict__`, and then reconstructed
            # via `type(**d)` from the (unwrapped) properties (bar empty input types, see next comment).
            o_typ = Output.all(**val.__dict__).apply(
                # if __dict__ was empty `all` will return an empty list object rather than a dict object,
                # there isn't really a good way to express this in mypy so the type checker doesn't pickup on
                # this. If we get an empty list we can't splat it as that results in a type error, so check
                # that we have some values before splatting. If it's empty just call the `typ` constructor
                # directly with no arguments.
                lambda d: typ(**d) if d else typ()
            )
            return cast(Output[U], o_typ)

        # Is a (non-empty) dict, list, or tuple? Recurse into the values within them.
        if val and isinstance(val, dict):
            # The keys themselves might be outputs, so we can't just pass `**val` to all.

            # keys() and values() will be in the same order: https://docs.python.org/3/library/stdtypes.html#dictionary-view-objects
            keys = list(val.keys())
            values = list(val.values())

            def liftValues(keys: List[Any]):
                d = {keys[i]: values[i] for i in range(len(keys))}
                return Output.all(**d)

            o_dict: Output[dict] = Output.all(*keys).apply(liftValues)
            return cast(Output[U], o_dict)

        if val and isinstance(val, list):
            o_list: Output[list] = Output.all(*val)
            return cast(Output[U], o_list)

        if val and isinstance(val, tuple):
            # We can splat a tuple into all, but we'll always get back a list...
            o_list = Output.all(*val)
            # ...so we need to convert back to a tuple.
            return cast(Output[U], o_list.apply(tuple))

        # If it's not an output, tuple, list, or dict, it must be known and not secret
        is_known_fut: asyncio.Future[bool] = asyncio.Future()
        is_secret_fut: asyncio.Future[bool] = asyncio.Future()
        is_known_fut.set_result(True)
        is_secret_fut.set_result(False)

        # Is it awaitable? If so, schedule it for execution and use the resulting future
        # as the value future for a new output.
        if isawaitable(val):
            val_fut = cast(asyncio.Future, val)
            promise_output = Output(
                set(), asyncio.ensure_future(val_fut), is_known_fut, is_secret_fut
            )
            return promise_output.apply(Output.from_input, True)

        # Is it a prompt value? Set up a new resolved future and use that as the value future.
        value_fut: asyncio.Future[Any] = asyncio.Future()
        value_fut.set_result(val)
        return Output(set(), value_fut, is_known_fut, is_secret_fut)

    @staticmethod
    def _from_input_shallow(val: Input[U]) -> "Output[U]":
        """
        Like `from_input`, but does not recur deeply. Instead, checks if `val` is an `Output` value
        and returns it as is. Otherwise, promotes a known value or future to `Output`.

        :param Input[T] val: An Input to be converted to an Output.
        :return: An Output corresponding to `val`.
        :rtype: Output[T]
        """

        if isinstance(val, Output):
            return val

        # If it's not an output, it must be known and not secret
        is_known_fut: asyncio.Future[bool] = asyncio.Future()
        is_secret_fut: asyncio.Future[bool] = asyncio.Future()
        is_known_fut.set_result(True)
        is_secret_fut.set_result(False)

        if isawaitable(val):
            val_fut = cast(asyncio.Future, val)
            return Output(
                set(), asyncio.ensure_future(val_fut), is_known_fut, is_secret_fut
            )

        # Is it a prompt value? Set up a new resolved future and use that as the value future.
        value_fut: asyncio.Future[Any] = asyncio.Future()
        value_fut.set_result(val)
        return Output(set(), value_fut, is_known_fut, is_secret_fut)

    @staticmethod
    def unsecret(val: "Output[U]") -> "Output[U]":
        """
        Takes an existing Output, deeply unwraps the nested values and returns a new Output without any secrets included

        :param Output[T] val: An Output to be converted to a non-Secret Output.
        :return: A deeply-unwrapped Output that is guaranteed to not contain any secret values.
        :rtype: Output[T]
        """
        is_secret: asyncio.Future[bool] = asyncio.Future()
        is_secret.set_result(False)
        return Output(val._resources, val._future, val._is_known, is_secret)

    @staticmethod
    def secret(val: Input[U]) -> "Output[U]":
        """
        Takes an Input value and produces an Output value from it, deeply unwrapping nested Input values as necessary
        given the type. It also marks the returned Output as a secret, so its contents will be persisted in an encrypted
        form in state files.

        :param Input[T] val: An Input to be converted to an Secret Output.
        :return: A deeply-unwrapped Output that is guaranteed to not contain any Input values and is marked as a Secret.
        :rtype: Output[T]
        """

        o = Output.from_input(val)
        is_secret: asyncio.Future[bool] = asyncio.Future()
        is_secret.set_result(True)
        return Output(o._resources, o._future, o._is_known, is_secret)

    # According to mypy these overloads unsafely overlap, so we ignore the type check.
    # https://mypy.readthedocs.io/en/stable/more_types.html#type-checking-the-variants:~:text=considered%20unsafely%20overlapping
    @overload
    @staticmethod
    def all(*args: "Output[Any]") -> "Output[List[Any]]": ...  # type: ignore

    @overload
    @staticmethod
    def all(**kwargs: "Output[Any]") -> "Output[Dict[str, Any]]": ...  # type: ignore

    @overload
    @staticmethod
    def all(*args: Input[Any]) -> "Output[List[Any]]": ...  # type: ignore

    @overload
    @staticmethod
    def all(**kwargs: Input[Any]) -> "Output[Dict[str, Any]]": ...  # type: ignore

    @staticmethod
    def all(
        *args: Input[Any], **kwargs: Input[Any]
    ) -> "Output[List[Any] | Dict[str, Any]]":
        """
        Produces an Output of a list (if args i.e a list of inputs are supplied)
        or dict (if kwargs i.e. keyworded arguments are supplied).

        This function can be used to combine multiple, separate Inputs into a single
        Output which can then be used as the target of `apply`. Resource dependencies
        are preserved in the returned Output.

        Examples::

            Output.all(foo, bar) -> Output[[foo, bar]]
            Output.all(foo=foo, bar=bar) -> Output[{"foo": foo, "bar": bar}]

        :param Input[T] args: A list of Inputs to convert.
        :param Input[T] kwargs: A list of named Inputs to convert.
        :return: An output of list or dict, converted from unnamed or named Inputs respectively.
        """

        # Three asynchronous helper functions to assist in the implementation:
        # is_known, which returns True if all of the input's values are known,
        # and false if any of them are not known,
        async def is_known(outputs: list):
            is_known_futures = [o._is_known for o in outputs]
            each_is_known = await asyncio.gather(*is_known_futures)
            return all(each_is_known)

        # is_secret, which returns True if any of the input values are secret, and
        # false if none of them are secret.
        async def is_secret(outputs: list):
            is_secret_futures = [o._is_secret for o in outputs]
            each_is_secret = await asyncio.gather(*is_secret_futures)
            return any(each_is_secret)

        async def get_resources(outputs: list):
            resources_futures = [o._resources for o in outputs]
            resources_agg = await asyncio.gather(*resources_futures)
            # Merge the list of resource dependencies across all inputs.
            return reduce(lambda acc, r: acc.union(r), resources_agg, set())

        # gather_futures, which aggregates the list or dict of futures in each input to a future of a list or dict.
        async def gather_futures(outputs: Union[dict, list]):
            if isinstance(outputs, list):
                value_futures_list = [
                    asyncio.ensure_future(o.future(with_unknowns=True)) for o in outputs
                ]
                return await asyncio.gather(*value_futures_list)
            value_futures_dict = {
                k: asyncio.ensure_future(v.future(with_unknowns=True))
                for k, v in outputs.items()
            }
            return await _gather_from_dict(value_futures_dict)

        if args and kwargs:
            raise ValueError(
                "Output.all() was supplied a mix of named and unnamed inputs"
            )
        # First, map all inputs to outputs using `from_input`.
        all_outputs: Union[list, dict] = (
            {k: Output.from_input(v) for k, v in kwargs.items()}
            if kwargs
            else [Output.from_input(x) for x in args]
        )

        # Aggregate the list or dict of futures into a future of list or dict.
        value_futures = asyncio.ensure_future(gather_futures(all_outputs))

        # Aggregate whether or not this output is known.
        output_values = (
            [all_outputs[k] for k in all_outputs]
            if isinstance(all_outputs, dict)
            else all_outputs
        )
        resources_futures = asyncio.ensure_future(get_resources(output_values))
        known_futures = asyncio.ensure_future(is_known(output_values))
        secret_futures = asyncio.ensure_future(is_secret(output_values))
        return Output(resources_futures, value_futures, known_futures, secret_futures)

    @staticmethod
    def concat(*args: Input[str]) -> "Output[str]":
        """
        Concatenates a collection of Input[str] into a single Output[str].

        This function takes a sequence of Input[str], stringifies each, and concatenates all values
        into one final string. This can be used like so:

            url = Output.concat("http://", server.hostname, ":", loadBalancer.port)

        :param Input[str] args: A list of string Inputs to concatenate.
        :return: A concatenated output string.
        :rtype: Output[str]
        """

        transformed_items: List[Input[Any]] = [Output.from_input(v) for v in args]
        # invariant http://mypy.readthedocs.io/en/latest/common_issues.html#variance
        return Output.all(*transformed_items).apply("".join)  # type: ignore

    @staticmethod
    def format(
        format_string: Input[str], *args: Input[object], **kwargs: Input[object]
    ) -> "Output[str]":
        """
        Perform a string formatting operation.

        This has the same semantics as `str.format` except it handles Input types.

        :param Input[str] format_string: A formatting string
        :param Input[object] args: Positional arguments for the format string
        :param Input[object] kwargs: Keyword arguments for the format string
        :return: A formatted output string.
        :rtype: Output[str]
        """

        if args and kwargs:
            return _map3_output(
                Output.from_input(format_string),
                Output.all(*args),
                Output.all(**kwargs),
                lambda str, args, kwargs: str.format(*args, **kwargs),
            )
        if args:
            return _map2_output(
                Output.from_input(format_string),
                Output.all(*args),
                lambda str, args: str.format(*args),
            )
        if kwargs:
            return _map2_output(
                Output.from_input(format_string),
                Output.all(**kwargs),
                lambda str, kwargs: str.format(**kwargs),
            )
        return Output.from_input(format_string).apply(lambda str: str.format())

    @staticmethod
    def json_dumps(
        obj: Input[Any],
        *,
        skipkeys: bool = False,
        ensure_ascii: bool = True,
        check_circular: bool = True,
        allow_nan: bool = True,
        cls: Optional[Type[json.JSONEncoder]] = None,
        indent: Optional[Union[int, str]] = None,
        separators: Optional[Tuple[str, str]] = None,
        default: Optional[Callable[[Any], Any]] = None,
        sort_keys: bool = False,
        **kw: Any,
    ) -> "Output[str]":
        """
        Uses json.dumps to serialize the given Input[object] value into a JSON string.

        The arguments have the same meaning as in `json.dumps` except obj is an Input.
        """

        if cls is None:
            cls = json.JSONEncoder

        output = Output.from_input(obj)
        result_resources: asyncio.Future[Set["Resource"]] = asyncio.Future()
        result_is_known: asyncio.Future[bool] = asyncio.Future()
        result_is_secret: asyncio.Future[bool] = asyncio.Future()

        async def run() -> str:
            resources: Set["Resource"] = set()
            try:
                seen_unknown = False
                seen_secret = False
                seen_resources = set()

                class OutputEncoder(cls):  # type: ignore
                    def default(self, o):
                        if isinstance(o, Output):
                            nonlocal seen_unknown
                            nonlocal seen_secret
                            nonlocal seen_resources

                            # We need to synchronously wait for o to complete
                            async def wait_output() -> Tuple[object, bool, bool, set]:
                                return (
                                    await o._future,
                                    await o._is_known,
                                    await o._is_secret,
                                    await o._resources,
                                )

                            (result, known, secret, resources) = _sync_await(
                                asyncio.ensure_future(wait_output())
                            )
                            # Update the secret flag and set of seen resources
                            seen_secret = seen_secret or secret
                            seen_resources.update(resources)
                            if known:
                                return result
                            # The value wasn't known set the local seenUnknown variable and just return None
                            # so the serialization doesn't raise an exception at this point
                            seen_unknown = True
                            return None

                        return super().default(o)

                # Await the output's details.
                resources = await output._resources
                is_known = await output._is_known
                is_secret = await output._is_secret
                value = await output._future

                if not is_known:
                    result_resources.set_result(resources)
                    result_is_known.set_result(is_known)
                    result_is_secret.set_result(is_secret)
                    return cast(str, None)

                # Try and dump using our special OutputEncoder to handle nested outputs
                result = json.dumps(
                    value,
                    skipkeys=skipkeys,
                    ensure_ascii=ensure_ascii,
                    check_circular=check_circular,
                    allow_nan=allow_nan,
                    cls=OutputEncoder,
                    indent=indent,
                    separators=separators,
                    default=default,
                    sort_keys=sort_keys,
                    **kw,
                )

                # Update the final resources and secret flag based on what we saw while dumping
                is_secret = is_secret or seen_secret
                resources = set(resources)
                resources.update(seen_resources)

                # If we saw an unknown during dumping then throw away the result and return not known
                if seen_unknown:
                    result_resources.set_result(resources)
                    result_is_known.set_result(False)
                    result_is_secret.set_result(is_secret)
                    return cast(str, None)

                result_resources.set_result(resources)
                result_is_known.set_result(True)
                result_is_secret.set_result(is_secret)
                return result

            finally:
                with contextlib.suppress(asyncio.InvalidStateError):
                    result_resources.set_result(resources)

                with contextlib.suppress(asyncio.InvalidStateError):
                    result_is_known.set_result(False)

                with contextlib.suppress(asyncio.InvalidStateError):
                    result_is_secret.set_result(False)

        run_fut = asyncio.ensure_future(run())
        return Output(result_resources, run_fut, result_is_known, result_is_secret)

    @staticmethod
    def json_loads(
        s: Input[Union[str, bytes, bytearray]],
        *,
        cls: Optional[Type[json.JSONDecoder]] = None,
        object_hook: Optional[Callable[[Dict[Any, Any]], Any]] = None,
        parse_float: Optional[Callable[[str], Any]] = None,
        parse_int: Optional[Callable[[str], Any]] = None,
        parse_constant: Optional[Callable[[str], Any]] = None,
        object_pairs_hook: Optional[Callable[[List[Tuple[Any, Any]]], Any]] = None,
        **kwds: Any,
    ) -> "Output[Any]":
        """
        Uses json.loads to deserialize the given JSON Input[str] value into a value.

        The arguments have the same meaning as in `json.loads` except s is an Input.
        """

        def loads(s: Union[str, bytes, bytearray]) -> Any:
            return json.loads(
                s,
                cls=cls,
                object_hook=object_hook,
                parse_float=parse_float,
                parse_int=parse_int,
                parse_constant=parse_constant,
                object_pairs_hook=object_pairs_hook,
                **kwds,
            )

        # You'd think this could all be on one line but mypy seems to think `s` is a `Sequence[object]` if you
        # do.
        s_output: Output[Union[str, bytes, bytearray]] = Output.from_input(s)
        return s_output.apply(loads)

    def __str__(self) -> str:
        err = _OutputToStringError()
        if os.getenv("PULUMI_ERROR_OUTPUT_STRING", "").lower() in ["1", "true"]:
            raise err
        msg = str(err)
        log.warn(msg)
        msg += "\nThis function may throw in a future version of Pulumi."
        return msg


class Unknown:
    """
    Unknown represents a value that is unknown.
    """

    def __init__(self):
        pass


UNKNOWN = Unknown()
"""
UNKNOWN is the singleton unknown value.
"""


def contains_unknowns(val: Any) -> bool:
    return rpc.contains_unknowns(val)


def _is_prompt(value: Input[T]) -> bool:
    """Checks if the value is prompty available."""

    return not isawaitable(value) and not isinstance(value, Output)


def _map_output(o: Output[T], transform: Callable[[T], U]) -> Output[U]:
    """Transforms an output's result value with a pure function."""

    async def fut() -> U:
        value = await o.future()
        return transform(value) if value is not None else cast(U, UNKNOWN)

    return Output(
        resources=o.resources(),
        future=asyncio.ensure_future(fut()),
        is_known=o.is_known(),
        is_secret=o.is_secret(),
    )


def _map2_output(
    o1: Output[T1], o2: Output[T2], transform: Callable[[T1, T2], U]
) -> Output[U]:
    """
    Joins two outputs and transforms their result with a pure function.
    Similar to `all` but does not deeply await.
    """

    async def fut() -> U:
        v1 = await o1.future()
        v2 = await o2.future()
        return (
            transform(v1, v2)
            if (v1 is not None) and (v2 is not None)
            else cast(U, UNKNOWN)
        )

    async def res() -> Set["Resource"]:
        r1 = await o1.resources()
        r2 = await o2.resources()
        return r1 | r2

    return Output(
        resources=asyncio.ensure_future(res()),
        future=asyncio.ensure_future(fut()),
        is_known=o1.is_known() and o2.is_known(),
        is_secret=o2.is_secret() or o2.is_secret(),
    )


def _map3_output(
    o1: Output[T1], o2: Output[T2], o3: Output[T3], transform: Callable[[T1, T2, T3], U]
) -> Output[U]:
    """
    Joins three outputs and transforms their result with a pure function.
    Similar to `all` but does not deeply await.
    """

    async def fut() -> U:
        v1 = await o1.future()
        v2 = await o2.future()
        v3 = await o3.future()
        return (
            transform(v1, v2, v3)
            if (v1 is not None) and (v2 is not None) and (v3 is not None)
            else cast(U, UNKNOWN)
        )

    async def res() -> Set["Resource"]:
        r1 = await o1.resources()
        r2 = await o2.resources()
        r3 = await o3.resources()
        return r1 | r2 | r3

    return Output(
        resources=asyncio.ensure_future(res()),
        future=asyncio.ensure_future(fut()),
        is_known=o1.is_known() and o2.is_known() and o3.is_known(),
        is_secret=o2.is_secret() or o2.is_secret() or o3.is_secret(),
    )


def _map_input(i: Input[T], transform: Callable[[T], U]) -> Input[U]:
    """Transforms an input's result value with a pure function."""

    if _is_prompt(i):
        return transform(cast(T, i))

    if isawaitable(i):
        inp = cast(Awaitable[T], i)

        async def fut() -> U:
            return transform(await inp)

        return asyncio.ensure_future(fut())

    return _map_output(cast(Output[T], i), transform)


def _map2_input(
    i1: Input[T1], i2: Input[T2], transform: Callable[[T1, T2], U]
) -> Input[U]:
    """
    Joins two inputs and transforms their result with a pure function.
    """

    if _is_prompt(i1):
        v1 = cast(T1, i1)
        return _map_input(i2, lambda v2: transform(v1, v2))

    if _is_prompt(i2):
        v2 = cast(T2, i2)
        return _map_input(i1, lambda v1: transform(v1, v2))

    if isawaitable(i1) and isawaitable(i2):
        a1 = cast(Awaitable[T1], i1)
        a2 = cast(Awaitable[T2], i2)

        async def join() -> U:
            v1 = await a1
            v2 = await a2
            return transform(v1, v2)

        return asyncio.ensure_future(join())

    return _map2_output(
        Output._from_input_shallow(i1), Output._from_input_shallow(i2), transform
    )


async def _gather_from_dict(tasks: dict) -> dict:
    results = await asyncio.gather(*tasks.values())
    return dict(zip(tasks.keys(), results))


def deferred_output() -> Tuple[Output[T], Callable[[Output[T]], None]]:
    """
    Creates an Output[T] whose value can be later resolved from another Output[T] instance.
    """
    # Setup the futures for the output.
    resolve_value: "asyncio.Future" = asyncio.Future()
    resolve_is_known: "asyncio.Future[bool]" = asyncio.Future()
    resolve_is_secret: "asyncio.Future[bool]" = asyncio.Future()
    resolve_deps: "asyncio.Future[Set[Resource]]" = asyncio.Future()
    already_resolved = False

    def resolve(o: Output[T]) -> None:
        nonlocal resolve_value
        nonlocal resolve_is_known
        nonlocal resolve_is_secret
        nonlocal resolve_deps
        nonlocal already_resolved
        if already_resolved:
            raise Exception("Deferred Output has already been resolved")
        already_resolved = True

        def value_callback(fut: asyncio.Future) -> None:
            if fut.exception() is not None:
                resolve_value.set_exception(fut.exception())  # type: ignore
            else:
                resolve_value.set_result(fut.result())

        asyncio.ensure_future(o.future()).add_done_callback(value_callback)

        def is_known_callback(fut: "asyncio.Future[bool]") -> None:
            if fut.exception() is not None:
                resolve_is_known.set_exception(fut.exception())  # type: ignore
            else:
                resolve_is_known.set_result(fut.result())

        asyncio.ensure_future(o.is_known()).add_done_callback(is_known_callback)

        def is_secret_callback(fut: "asyncio.Future[bool]") -> None:
            if fut.exception() is not None:
                resolve_is_secret.set_exception(fut.exception())  # type: ignore
            else:
                resolve_is_secret.set_result(fut.result())

        asyncio.ensure_future(o.is_secret()).add_done_callback(is_secret_callback)

        def deps_callback(fut: "asyncio.Future[Set[Resource]]") -> None:
            if fut.exception() is not None:
                resolve_deps.set_exception(fut.exception())  # type: ignore
            else:
                resolve_deps.set_result(fut.result())

        asyncio.ensure_future(o.resources()).add_done_callback(deps_callback)

    out = Output(resolve_deps, resolve_value, resolve_is_known, resolve_is_secret)
    return out, resolve


class _OutputToStringError(Exception):
    """_OutputToStringError is the class of errors raised when __str__ is called
    on a Pulumi Output."""

    def __init__(self) -> None:
        super().__init__(
            """Calling __str__ on an Output[T] is not supported.

To get the value of an Output[T] as an Output[str] consider:
1. o.apply(lambda v: f"prefix{v}suffix")

See https://www.pulumi.com/docs/concepts/inputs-outputs for more details."""
        )


def _safe_str(v: Any) -> str:
    """_safe_str returns the string representation of v if possible. If v is an
    Output, _safe_str returns a fallback string, whether it's able to detect an
    Output ahead of time or not by catching the _OutputToStringError. _safe_str
    is designed for use in e.g. logging and debugging contexts where it's useful
    to print all the information that can be reasonably obtained, without
    falling afoul of things like PULUMI_ERROR_OUTPUT_STRING."""

    # This is not a perfect implementation. If v's __str__ method tries to
    # stringify an Output, and PULUMI_ERROR_OUTPUT_STRING is not set, we'll
    # still produce an ugly message somwhere inside the resulting string. If
    # this becomes an issue, we could spot it using e.g. string comparison or
    # (far uglier but potentially more performant) monkey patching/subclassing
    # the strings involved. For now this feels like a sensible compromise.

    if isinstance(v, Output):
        return "Output[T]"

    try:
        return str(v)
    except _OutputToStringError:
        return "Output[T]"
