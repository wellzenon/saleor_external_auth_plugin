from functools import reduce
from inspect import getmembers, ismodule
from typing import Any, Callable, List, Union
from types import ModuleType

NoneType = type(None)


def pipe(first: Any, *list: List[Callable[[Any], Any]]) -> Any:
    if callable(first):
        return lambda x: reduce(lambda f, g: g(f), [first, *list], x)
    return reduce(lambda f, g: g(f), list, first)


def dict_keys_to_lower(kmap: dict) -> dict:
    return reduce(
        lambda f, g: {**f, **g},
        map(
            lambda k: {
                k.lower(): kmap[k]
                if not isinstance(kmap[k], dict)
                else dict_keys_to_lower(kmap[k])
            },
            kmap,
        ),
    )


def get_submodule(
    main_module: List[Any],
) -> Callable[[str], Union[ModuleType, NoneType]]:
    """Get the submodule_name submodule from the main_module
    i.e.: if submodule_name is 'facebook' then will return
    the facebook submodule from main_module or None"""

    def get_module_by_name(submodule_name: str) -> Union[ModuleType, NoneType]:
        def filter_fn(submodule):
            return (
                ismodule(submodule)
                and submodule.__name__.split(".")[-1] == submodule_name
            )

        submodule = getmembers(main_module, filter_fn)

        if len(submodule):
            return submodule[0][1]

        return None

    return get_module_by_name


def make_uri(path: str) -> Callable[[dict], str]:
    """Contrucs a URI through a initial 'path' and
    a dict of 'params' key value pairs"""

    def join_params(params: dict) -> str:
        return (
            f"{path}?" + "".join(f"{k}={v}&" for k, v in params.items())[:-1]
            if params
            else path
        )

    return join_params


def instantiate(type_class: type) -> Callable[[Union[dict, any]], Any]:
    """Try to instantiate 'type_class' in all possible values inside 'value'
    if it's a dict will recursively try to build 'type_class' in all nested values
    if can't instatiate 'type_class', then just returns 'value'"""

    def instantiate_type_class(value: Union[dict, any]) -> Any:
        try:
            return type_class(**value)
        except:
            if type(value) == dict:
                return reduce(
                    lambda acc, item: {**acc, item[0]: instantiate_type_class(item[1])},
                    value.items(),
                    {},
                )
            return value

    return instantiate_type_class


def dict_str_lookup(search: str) -> Callable[[dict], str]:
    """returns the first string containing 'search' from all fields in 'dict' including nested"""

    def lookup(_dict: dict) -> str:
        for value in _dict.values():
            if isinstance(value, str) and search in value:
                return value
            nested = lookup(value) if isinstance(value, dict) else None
            if nested:
                return nested

    return lookup
