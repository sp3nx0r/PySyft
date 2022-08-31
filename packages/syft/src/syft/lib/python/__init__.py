# stdlib
from typing import Any as AnyAny
from typing import Optional
from typing import cast

# relative
from . import collections
from ...ast import add_classes
from ...ast import add_dynamic_objects
from ...ast import add_methods
from ...ast import add_modules
from ...ast.globals import Globals
from ...core.common.serde import _deserialize
from ...core.common.serde import _serialize
from ...core.common.serde.recursive import recursive_serde_register
from ...core.node.abstract.node import AbstractNodeClient
from ..misc.union import UnionGenerator
from .bool import Bool
from .bytes import Bytes
from .collections import SyOrderedDict
from .complex import Complex
from .dict import Dict
from .float import Float
from .int import Int
from .iterator import Iterator
from .list import List
from .none import SyNone
from .none import _SyNone
from .primitive_container import Any
from .primitive_interface import PyPrimitive
from .range import Range
from .set import Set
from .slice import Slice
from .string import String
from .tuple import Tuple
from .util import downcast

SyTypes = [
    Bool,
    Complex,
    Dict,
    Float,
    Int,
    SyNone,
    _SyNone,
    Any,
    PyPrimitive,
    Slice,
    String,
    Tuple,
    Bytes,
    List,
    Set,
    Range,
    SyOrderedDict,
]

# TODO Tudor: FIX THIS, we can't rely on _serialize/_deserialize like this (I think)


def serialize(x: AnyAny) -> bytes:
    new_id = getattr(x, "id", None)
    if hasattr(x, "upcast"):
        x = x.upcast()
    return cast(bytes, _serialize((x, new_id), to_bytes=True))


def deserialize(x: bytes) -> AnyAny:
    up_obj, old_id = _deserialize(x, from_bytes=True)
    new_obj = downcast(up_obj)
    if old_id:
        new_obj._id = old_id
    return new_obj


for syft_type in SyTypes:
    syft_type.__module__ = __name__

    recursive_serde_register(syft_type, serialize=serialize, deserialize=deserialize)


def create_python_ast(client: Optional[AbstractNodeClient] = None) -> Globals:
    ast = Globals(client)

    modules = ["syft", "syft.lib", "syft.lib.python", "syft.lib.python.collections"]
    classes = [
        ("syft.lib.python.Bytes", "syft.lib.python.Bytes", Bytes),
        ("syft.lib.python.Bool", "syft.lib.python.Bool", Bool),
        ("syft.lib.python.Complex", "syft.lib.python.Complex", Complex),
        ("syft.lib.python.Dict", "syft.lib.python.Dict", Dict),
        ("syft.lib.python.Float", "syft.lib.python.Float", Float),
        ("syft.lib.python.Int", "syft.lib.python.Int", Int),
        ("syft.lib.python.List", "syft.lib.python.List", List),
        ("syft.lib.python.Slice", "syft.lib.python.Slice", Slice),
        ("syft.lib.python.Range", "syft.lib.python.Range", Range),
        ("syft.lib.python.String", "syft.lib.python.String", String),
        ("syft.lib.python._SyNone", "syft.lib.python._SyNone", _SyNone),
        ("syft.lib.python.PyPrimitive", "syft.lib.python.PyPrimitive", PyPrimitive),
        ("syft.lib.python.Any", "syft.lib.python.Any", Any),
        ("syft.lib.python.Tuple", "syft.lib.python.Tuple", Tuple),
        ("syft.lib.python.Iterator", "syft.lib.python.Iterator", Iterator),
        ("syft.lib.python.Set", "syft.lib.python.Set", Set),
        (
            "syft.lib.python.collections.SyOrderedDict",
            "syft.lib.python.collections.SyOrderedDict",
            collections.SyOrderedDict,
        ),
    ]

    methods = [
        # Range methods - quite there
        ("syft.lib.python.Range.__eq__", "syft.lib.python.Bool"),
        ("syft.lib.python.Range.__ge__", "syft.lib.python.Bool"),
        ("syft.lib.python.Range.__gt__", "syft.lib.python.Bool"),
        ("syft.lib.python.Range.__le__", "syft.lib.python.Bool"),
        ("syft.lib.python.Range.__lt__", "syft.lib.python.Bool"),
        ("syft.lib.python.Range.__ne__", "syft.lib.python.Bool"),
        ("syft.lib.python.Range.__bool__", "syft.lib.python.Bool"),
        ("syft.lib.python.Range.__contains__", "syft.lib.python.Bool"),
        ("syft.lib.python.Range.__getitem__", "syft.lib.python.Any"),
        ("syft.lib.python.Range.__len__", "syft.lib.python.Int"),
        ("syft.lib.python.Range.__iter__", "syft.lib.python.Iterator"),
        ("syft.lib.python.Range.__sizeof__", "syft.lib.python.Int"),
        (
            "syft.lib.python.Range.start",
            UnionGenerator["syft.lib.python.Int", "syft.lib.python._SyNone"],
        ),
        (
            "syft.lib.python.Range.step",
            UnionGenerator["syft.lib.python.Int", "syft.lib.python._SyNone"],
        ),
        (
            "syft.lib.python.Range.stop",
            UnionGenerator["syft.lib.python.Int", "syft.lib.python._SyNone"],
        ),
        (
            "syft.lib.python.Range.count",
            UnionGenerator["syft.lib.python.Int", "syft.lib.python._SyNone"],
        ),
        (
            "syft.lib.python.Range.index",
            UnionGenerator["syft.lib.python.Int", "syft.lib.python._SyNone"],
        ),
        # Slice methods - quite there
        ("syft.lib.python.Slice.__eq__", "syft.lib.python.Bool"),
        ("syft.lib.python.Slice.__ge__", "syft.lib.python.Bool"),
        ("syft.lib.python.Slice.__gt__", "syft.lib.python.Bool"),
        ("syft.lib.python.Slice.__le__", "syft.lib.python.Bool"),
        ("syft.lib.python.Slice.__lt__", "syft.lib.python.Bool"),
        ("syft.lib.python.Slice.__ne__", "syft.lib.python.Bool"),
        ("syft.lib.python.Slice.__str__", "syft.lib.python.String"),
        ("syft.lib.python.Slice.indices", "syft.lib.python.Tuple"),
        (
            "syft.lib.python.Slice.start",
            UnionGenerator["syft.lib.python.Int", "syft.lib.python._SyNone"],
        ),
        (
            "syft.lib.python.Slice.step",
            UnionGenerator["syft.lib.python.Int", "syft.lib.python._SyNone"],
        ),
        (
            "syft.lib.python.Slice.stop",
            UnionGenerator["syft.lib.python.Int", "syft.lib.python._SyNone"],
        ),
        # List methods - quite there
        ("syft.lib.python.List.__len__", "syft.lib.python.Int"),
        ("syft.lib.python.List.__getitem__", "syft.lib.python.Any"),
        ("syft.lib.python.List.__iter__", "syft.lib.python.Iterator"),
        ("syft.lib.python.List.__add__", "syft.lib.python.List"),
        ("syft.lib.python.List.append", "syft.lib.python._SyNone"),
        ("syft.lib.python.List.__gt__", "syft.lib.python.Bool"),
        ("syft.lib.python.List.__lt__", "syft.lib.python.Bool"),
        ("syft.lib.python.List.__le__", "syft.lib.python.Bool"),
        ("syft.lib.python.List.__ge__", "syft.lib.python.Bool"),
        ("syft.lib.python.List.__iadd__", "syft.lib.python.List"),
        ("syft.lib.python.List.__imul__", "syft.lib.python.List"),
        ("syft.lib.python.List.__iadd__", "syft.lib.python.List"),
        ("syft.lib.python.List.__contains__", "syft.lib.python.Bool"),
        ("syft.lib.python.List.__delattr__", "syft.lib.python.None"),
        ("syft.lib.python.List.__delitem__", "syft.lib.python.None"),
        ("syft.lib.python.List.__eq__", "syft.lib.python.Bool"),
        ("syft.lib.python.List.__mul__", "syft.lib.python.List"),
        ("syft.lib.python.List.__ne__", "syft.lib.python.Bool"),
        ("syft.lib.python.List.__sizeof__", "syft.lib.python.Int"),
        ("syft.lib.python.List.__len__", "syft.lib.python.Int"),
        ("syft.lib.python.List.__getitem__", "syft.lib.python.Any"),
        ("syft.lib.python.List.__setitem__", "syft.lib.python._SyNone"),
        ("syft.lib.python.List.__rmul__", "syft.lib.python.List"),
        ("syft.lib.python.List.copy", "syft.lib.python.List"),
        ("syft.lib.python.List.count", "syft.lib.python.Int"),
        ("syft.lib.python.List.sort", "syft.lib.python._SyNone"),
        ("syft.lib.python.List.reverse", "syft.lib.python._SyNone"),
        ("syft.lib.python.List.remove", "syft.lib.python._SyNone"),
        ("syft.lib.python.List.pop", "syft.lib.python.Any"),
        ("syft.lib.python.List.index", "syft.lib.python.Any"),
        ("syft.lib.python.List.insert", "syft.lib.python._SyNone"),
        ("syft.lib.python.List.clear", "syft.lib.python._SyNone"),
        ("syft.lib.python.List.extend", "syft.lib.python._SyNone"),
        ("syft.lib.python.List.__reversed__", "syft.lib.python.Iterator"),
        ("syft.lib.python.List.__delitem__", "syft.lib.python._SyNone"),
        # Bool methods - quite there
        ("syft.lib.python.Bool.__abs__", "syft.lib.python.Int"),
        ("syft.lib.python.Bool.__eq__", "syft.lib.python.Bool"),
        ("syft.lib.python.Bool.__add__", "syft.lib.python.Int"),
        ("syft.lib.python.Bool.__and__", "syft.lib.python.Bool"),
        ("syft.lib.python.Bool.__ceil__", "syft.lib.python.Bool"),
        ("syft.lib.python.Bool.__divmod__", "syft.lib.python.Tuple"),
        ("syft.lib.python.Bool.__floor__", "syft.lib.python.Int"),
        ("syft.lib.python.Bool.__float__", "syft.lib.python.Float"),
        ("syft.lib.python.Bool.__floordiv__", "syft.lib.python.Int"),
        ("syft.lib.python.Bool.__ge__", "syft.lib.python.Bool"),
        ("syft.lib.python.Bool.__gt__", "syft.lib.python.Bool"),
        ("syft.lib.python.Bool.__invert__", "syft.lib.python.Int"),
        ("syft.lib.python.Bool.__le__", "syft.lib.python.Bool"),
        ("syft.lib.python.Bool.__lt__", "syft.lib.python.Bool"),
        ("syft.lib.python.Bool.__lshift__", "syft.lib.python.Int"),
        ("syft.lib.python.Bool.__mod__", "syft.lib.python.Int"),
        ("syft.lib.python.Bool.__mul__", "syft.lib.python.Int"),
        ("syft.lib.python.Bool.__ne__", "syft.lib.python.Bool"),
        ("syft.lib.python.Bool.__neg__", "syft.lib.python.Int"),
        ("syft.lib.python.Bool.__or__", "syft.lib.python.Bool"),
        ("syft.lib.python.Bool.__pos__", "syft.lib.python.Int"),
        ("syft.lib.python.Bool.__pow__", "syft.lib.python.Int"),
        ("syft.lib.python.Bool.__radd__", "syft.lib.python.Int"),
        ("syft.lib.python.Bool.__rand__", "syft.lib.python.Bool"),
        ("syft.lib.python.Bool.__rdivmod__", "syft.lib.python.Bool"),
        ("syft.lib.python.Bool.__rfloordiv__", "syft.lib.python.Bool"),
        ("syft.lib.python.Bool.__rlshift__", "syft.lib.python.Int"),
        ("syft.lib.python.Bool.__rmod__", "syft.lib.python.Int"),
        ("syft.lib.python.Bool.__rmul__", "syft.lib.python.Int"),
        ("syft.lib.python.Bool.__ror__", "syft.lib.python.Bool"),
        ("syft.lib.python.Bool.__round__", "syft.lib.python.Int"),
        ("syft.lib.python.Bool.__rpow__", "syft.lib.python.Int"),
        ("syft.lib.python.Bool.__rrshift__", "syft.lib.python.Int"),
        ("syft.lib.python.Bool.__rshift__", "syft.lib.python.Int"),
        ("syft.lib.python.Bool.__rsub__", "syft.lib.python.Int"),
        ("syft.lib.python.Bool.__rtruediv__", "syft.lib.python.Int"),
        ("syft.lib.python.Bool.__rxor__", "syft.lib.python.Int"),
        ("syft.lib.python.Bool.__sub__", "syft.lib.python.Int"),
        ("syft.lib.python.Bool.__truediv__", "syft.lib.python.Int"),
        ("syft.lib.python.Bool.__xor__", "syft.lib.python.Int"),
        ("syft.lib.python.Bool.__trunc__", "syft.lib.python.Int"),
        ("syft.lib.python.Bool.conjugate", "syft.lib.python.Int"),
        ("syft.lib.python.Bool.bit_length", "syft.lib.python.Int"),
        ("syft.lib.python.Bool.as_integer_ratio", "syft.lib.python.Tuple"),
        ("syft.lib.python.Bool.numerator", "syft.lib.python.Int"),
        ("syft.lib.python.Bool.real", "syft.lib.python.Int"),
        ("syft.lib.python.Bool.imag", "syft.lib.python.Int"),
        ("syft.lib.python.Bool.denominator", "syft.lib.python.Int"),
        # Float methods - subject to further change due
        ("syft.lib.python.Float.__add__", "syft.lib.python.Float"),
        ("syft.lib.python.Float.__truediv__", "syft.lib.python.Float"),
        ("syft.lib.python.Float.__divmod__", "syft.lib.python.Float"),
        ("syft.lib.python.Float.__eq__", "syft.lib.python.Bool"),
        ("syft.lib.python.Float.__ge__", "syft.lib.python.Bool"),
        ("syft.lib.python.Float.__lt__", "syft.lib.python.Bool"),
        ("syft.lib.python.Float.__le__", "syft.lib.python.Bool"),
        ("syft.lib.python.Float.__gt__", "syft.lib.python.Bool"),
        ("syft.lib.python.Float.__add__", "syft.lib.python.Float"),
        ("syft.lib.python.Float.__abs__", "syft.lib.python.Float"),
        ("syft.lib.python.Float.__bool__", "syft.lib.python.Bool"),
        ("syft.lib.python.Float.__sub__", "syft.lib.python.Float"),
        ("syft.lib.python.Float.__rsub__", "syft.lib.python.Float"),
        ("syft.lib.python.Float.__mul__", "syft.lib.python.Float"),
        ("syft.lib.python.Float.__rmul__", "syft.lib.python.Float"),
        ("syft.lib.python.Float.__divmod__", "syft.lib.python.Tuple"),
        ("syft.lib.python.Float.__int__", "syft.lib.python.Int"),
        ("syft.lib.python.Float.__neg__", "syft.lib.python.Float"),
        ("syft.lib.python.Float.__ne__", "syft.lib.python.Bool"),
        ("syft.lib.python.Float.__floordiv__", "syft.lib.python.Float"),
        ("syft.lib.python.Float.__truediv__", "syft.lib.python.Float"),
        ("syft.lib.python.Float.__mod__", "syft.lib.python.Float"),
        ("syft.lib.python.Float.__rmod__", "syft.lib.python.Float"),
        ("syft.lib.python.Float.__rdivmod__", "syft.lib.python.Tuple"),
        ("syft.lib.python.Float.__rfloordiv__", "syft.lib.python.Float"),
        ("syft.lib.python.Float.__round__", "syft.lib.python.Int"),
        ("syft.lib.python.Float.__rtruediv__", "syft.lib.python.Float"),
        ("syft.lib.python.Float.__sizeof__", "syft.lib.python.Int"),
        ("syft.lib.python.Float.__trunc__", "syft.lib.python.Int"),
        ("syft.lib.python.Float.as_integer_ratio", "syft.lib.python.Tuple"),
        ("syft.lib.python.Float.is_integer", "syft.lib.python.Bool"),
        ("syft.lib.python.Float.__pow__", "syft.lib.python.Float"),
        ("syft.lib.python.Float.__rpow__", "syft.lib.python.Float"),
        ("syft.lib.python.Float.__iadd__", "syft.lib.python.Float"),
        ("syft.lib.python.Float.__isub__", "syft.lib.python.Float"),
        ("syft.lib.python.Float.__imul__", "syft.lib.python.Float"),
        ("syft.lib.python.Float.__imod__", "syft.lib.python.Float"),
        ("syft.lib.python.Float.__ipow__", "syft.lib.python.Float"),
        ("syft.lib.python.Float.__pos__", "syft.lib.python.Float"),
        ("syft.lib.python.Float.conjugate", "syft.lib.python.Float"),
        ("syft.lib.python.Float.imag", "syft.lib.python.Int"),
        ("syft.lib.python.Float.real", "syft.lib.python.Float"),
        # String Methods
        ("syft.lib.python.String.__add__", "syft.lib.python.String"),
        ("syft.lib.python.String.__contains__", "syft.lib.python.Bool"),
        ("syft.lib.python.String.__eq__", "syft.lib.python.Bool"),
        ("syft.lib.python.String.__float__", "syft.lib.python.Float"),
        ("syft.lib.python.String.__ge__", "syft.lib.python.Bool"),
        ("syft.lib.python.String.__getitem__", "syft.lib.python.String"),
        ("syft.lib.python.String.__gt__", "syft.lib.python.Bool"),
        ("syft.lib.python.String.__int__", "syft.lib.python.Int"),
        ("syft.lib.python.String.__iter__", "syft.lib.python.Any"),
        ("syft.lib.python.String.__le__", "syft.lib.python.Bool"),
        ("syft.lib.python.String.__len__", "syft.lib.python.Int"),
        ("syft.lib.python.String.__lt__", "syft.lib.python.Bool"),
        ("syft.lib.python.String.__mod__", "syft.lib.python.String"),
        ("syft.lib.python.String.__mul__", "syft.lib.python.String"),
        ("syft.lib.python.String.__ne__", "syft.lib.python.Bool"),
        ("syft.lib.python.String.__reversed__", "syft.lib.python.String"),
        ("syft.lib.python.String.__sizeof__", "syft.lib.python.Int"),
        ("syft.lib.python.String.__str__", "syft.lib.python.String"),
        ("syft.lib.python.String.capitalize", "syft.lib.python.String"),
        ("syft.lib.python.String.casefold", "syft.lib.python.String"),
        ("syft.lib.python.String.center", "syft.lib.python.String"),
        ("syft.lib.python.String.count", "syft.lib.python.Int"),
        ("syft.lib.python.String.encode", "syft.lib.python.String"),
        ("syft.lib.python.String.expandtabs", "syft.lib.python.String"),
        ("syft.lib.python.String.find", "syft.lib.python.Int"),
        ("syft.lib.python.String.format", "syft.lib.python.String"),
        ("syft.lib.python.String.format_map", "syft.lib.python.String"),
        ("syft.lib.python.String.index", "syft.lib.python.Int"),
        ("syft.lib.python.String.isalnum", "syft.lib.python.Bool"),
        ("syft.lib.python.String.isalpha", "syft.lib.python.Bool"),
        ("syft.lib.python.String.isdecimal", "syft.lib.python.Bool"),
        ("syft.lib.python.String.isdigit", "syft.lib.python.Bool"),
        ("syft.lib.python.String.isidentifier", "syft.lib.python.Bool"),
        ("syft.lib.python.String.islower", "syft.lib.python.Bool"),
        ("syft.lib.python.String.isnumeric", "syft.lib.python.Bool"),
        ("syft.lib.python.String.isprintable", "syft.lib.python.Bool"),
        ("syft.lib.python.String.isspace", "syft.lib.python.Bool"),
        ("syft.lib.python.String.isupper", "syft.lib.python.Bool"),
        ("syft.lib.python.String.join", "syft.lib.python.String"),
        ("syft.lib.python.String.ljust", "syft.lib.python.String"),
        ("syft.lib.python.String.lower", "syft.lib.python.String"),
        ("syft.lib.python.String.lstrip", "syft.lib.python.String"),
        ("syft.lib.python.String.partition", "syft.lib.python.Tuple"),
        ("syft.lib.python.String.replace", "syft.lib.python.String"),
        ("syft.lib.python.String.rfind", "syft.lib.python.Int"),
        ("syft.lib.python.String.rindex", "syft.lib.python.Int"),
        ("syft.lib.python.String.rjust", "syft.lib.python.String"),
        ("syft.lib.python.String.rpartition", "syft.lib.python.Tuple"),
        ("syft.lib.python.String.rsplit", "syft.lib.python.List"),
        ("syft.lib.python.String.rstrip", "syft.lib.python.String"),
        ("syft.lib.python.String.split", "syft.lib.python.List"),
        ("syft.lib.python.String.splitlines", "syft.lib.python.List"),
        ("syft.lib.python.String.startswith", "syft.lib.python.Bool"),
        ("syft.lib.python.String.strip", "syft.lib.python.String"),
        ("syft.lib.python.String.swapcase", "syft.lib.python.String"),
        ("syft.lib.python.String.title", "syft.lib.python.String"),
        ("syft.lib.python.String.translate", "syft.lib.python.String"),
        ("syft.lib.python.String.upper", "syft.lib.python.String"),
        ("syft.lib.python.String.zfill", "syft.lib.python.String"),
        ("syft.lib.python.String.__contains__", "syft.lib.python.Bool"),
        ("syft.lib.python.String.__rmul__", "syft.lib.python.String"),
        ("syft.lib.python.String.endswith", "syft.lib.python.Bool"),
        ("syft.lib.python.String.isascii", "syft.lib.python.Bool"),
        ("syft.lib.python.String.istitle", "syft.lib.python.Bool"),
        # Dict methods
        ("syft.lib.python.Dict.__contains__", "syft.lib.python.Bool"),
        ("syft.lib.python.Dict.__eq__", "syft.lib.python.Bool"),
        ("syft.lib.python.Dict.__format__", "syft.lib.python.String"),
        ("syft.lib.python.Dict.__ge__", "syft.lib.python.Bool"),
        ("syft.lib.python.Dict.__getitem__", "syft.lib.python.Any"),
        ("syft.lib.python.Dict.__gt__", "syft.lib.python.Bool"),
        ("syft.lib.python.Dict.__iter__", "syft.lib.python.Iterator"),
        ("syft.lib.python.Dict.__le__", "syft.lib.python.Bool"),
        ("syft.lib.python.Dict.__len__", "syft.lib.python.Int"),
        ("syft.lib.python.Dict.__lt__", "syft.lib.python.Bool"),
        ("syft.lib.python.Dict.__ne__", "syft.lib.python.Bool"),
        ("syft.lib.python.Dict.__sizeof__", "syft.lib.python.Int"),
        ("syft.lib.python.Dict.__str__", "syft.lib.python.String"),
        ("syft.lib.python.Dict.copy", "syft.lib.python.Dict"),
        ("syft.lib.python.Dict.clear", "syft.lib.python._SyNone"),
        ("syft.lib.python.Dict.fromkeys", "syft.lib.python.Dict"),
        # Rename get to dict_get because of conflict
        ("syft.lib.python.Dict.dict_get", "syft.lib.python.Any"),
        ("syft.lib.python.Dict.items", "syft.lib.python.Iterator"),
        ("syft.lib.python.Dict.keys", "syft.lib.python.Iterator"),
        ("syft.lib.python.Dict.pop", "syft.lib.python.Any"),
        ("syft.lib.python.Dict.popitem", "syft.lib.python.Tuple"),
        ("syft.lib.python.Dict.setdefault", "syft.lib.python.Any"),
        ("syft.lib.python.Dict.values", "syft.lib.python.Iterator"),
        # Int methods - subject to further change
        ("syft.lib.python.Int.__add__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__truediv__", "syft.lib.python.Float"),
        ("syft.lib.python.Int.__divmod__", "syft.lib.python.Float"),
        ("syft.lib.python.Int.__floordiv__", "syft.lib.python.Float"),
        ("syft.lib.python.Int.__invert__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__abs__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__bool__", "syft.lib.python.Bool"),
        ("syft.lib.python.Int.__divmod__", "syft.lib.python.Tuple"),
        ("syft.lib.python.Int.__rdivmod__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__radd__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__sub__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__rsub__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__rtruediv__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__mul__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__rmul__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__ceil__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__eq__", "syft.lib.python.Bool"),
        ("syft.lib.python.Int.__float__", "syft.lib.python.Float"),
        ("syft.lib.python.Int.__floor__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__floordiv__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__rfloordiv__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__truediv__", "syft.lib.python.Float"),
        ("syft.lib.python.Int.__mod__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__rmod__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__pow__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__rpow__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__lshift__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__rlshift__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__round__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__rshift__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__rrshift__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__and__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__rand__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__xor__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__xor__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__rxor__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__or__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__ror__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__ge__", "syft.lib.python.Bool"),
        ("syft.lib.python.Int.__lt__", "syft.lib.python.Bool"),
        ("syft.lib.python.Int.__le__", "syft.lib.python.Bool"),
        ("syft.lib.python.Int.__gt__", "syft.lib.python.Bool"),
        ("syft.lib.python.Int.__iadd__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__isub__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__imul__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__ifloordiv__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__itruediv__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__imod__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__ipow__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__ne__", "syft.lib.python.Bool"),
        ("syft.lib.python.Int.__neg__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__pos__", "syft.lib.python.Int"),
        ("syft.lib.python.Int.as_integer_ratio", "syft.lib.python.Tuple"),
        ("syft.lib.python.Int.bit_length", "syft.lib.python.Int"),
        ("syft.lib.python.Int.denominator", "syft.lib.python.Int"),
        ("syft.lib.python.Int.from_bytes", "syft.lib.python.Int"),
        ("syft.lib.python.Int.real", "syft.lib.python.Int"),
        ("syft.lib.python.Int.imag", "syft.lib.python.Int"),
        ("syft.lib.python.Int.numerator", "syft.lib.python.Int"),
        ("syft.lib.python.Int.conjugate", "syft.lib.python.Int"),
        ("syft.lib.python.Int.__trunc__", "syft.lib.python.Int"),
        # Tuple
        ("syft.lib.python.Tuple.__add__", "syft.lib.python.Tuple"),
        ("syft.lib.python.Tuple.__contains__", "syft.lib.python.Bool"),
        ("syft.lib.python.Tuple.__ne__", "syft.lib.python.Bool"),
        ("syft.lib.python.Tuple.__ge__", "syft.lib.python.Bool"),
        ("syft.lib.python.Tuple.__gt__", "syft.lib.python.Bool"),
        ("syft.lib.python.Tuple.__le__", "syft.lib.python.Bool"),
        ("syft.lib.python.Tuple.__lt__", "syft.lib.python.Bool"),
        ("syft.lib.python.Tuple.__mul__", "syft.lib.python.Tuple"),
        ("syft.lib.python.Tuple.__rmul__", "syft.lib.python.Tuple"),
        ("syft.lib.python.Tuple.__len__", "syft.lib.python.Int"),
        ("syft.lib.python.Tuple.__getitem__", "syft.lib.python.Any"),
        ("syft.lib.python.Tuple.count", "syft.lib.python.Int"),
        ("syft.lib.python.Tuple.index", "syft.lib.python.Int"),
        ("syft.lib.python.Tuple.__iter__", "syft.lib.python.Iterator"),
        # PyContainer - quite there
        ("syft.lib.python.Any.__add__", "syft.lib.python.Any"),
        ("syft.lib.python.Any.__iter__", "syft.lib.python.Iterator"),
        ("syft.lib.python.Any.__next__", "syft.lib.python.Any"),
        ("syft.lib.python.Any.__len__", "syft.lib.python.Int"),
        ("syft.lib.python.Any.__radd__", "syft.lib.python.Any"),
        ("syft.lib.python.Any.__truediv__", "syft.lib.python.Any"),
        ("syft.lib.python.Any.__rtruediv__", "syft.lib.python.Any"),
        ("syft.lib.python.Any.__floordiv__", "syft.lib.python.Any"),
        ("syft.lib.python.Any.__rfloordiv__", "syft.lib.python.Any"),
        ("syft.lib.python.Any.__mul__", "syft.lib.python.Any"),
        ("syft.lib.python.Any.__rmul__", "syft.lib.python.Any"),
        ("syft.lib.python.Any.__sub__", "syft.lib.python.Any"),
        ("syft.lib.python.Any.__rsub__", "syft.lib.python.Any"),
        (
            "syft.lib.python.Iterator.__next__",
            UnionGenerator[
                "syft.lib.python.Int",
                "syft.lib.python.Float",
                "syft.lib.python.String",
                "torch.nn.Parameter",
                "torch.Tensor",
            ],
        ),  # temp until casting
        ("syft.lib.python.Iterator.__iter__", "syft.lib.python.Iterator"),
        ("syft.lib.python.Iterator.__len__", "syft.lib.python.Int"),
        ("syft.lib.python.Set.__and__", "syft.lib.python.Set"),
        ("syft.lib.python.Set.__contains__", "syft.lib.python.Bool"),
        ("syft.lib.python.Set.__eq__", "syft.lib.python.Bool"),
        ("syft.lib.python.Set.__ge__", "syft.lib.python.Bool"),
        ("syft.lib.python.Set.__gt__", "syft.lib.python.Bool"),
        ("syft.lib.python.Set.__iand__", "syft.lib.python.Set"),
        ("syft.lib.python.Set.__ior__", "syft.lib.python.Set"),
        ("syft.lib.python.Set.__isub__", "syft.lib.python.Set"),
        ("syft.lib.python.Set.__ixor__", "syft.lib.python.Set"),
        ("syft.lib.python.Set.__le__", "syft.lib.python.Bool"),
        ("syft.lib.python.Set.__len__", "syft.lib.python.Int"),
        ("syft.lib.python.Set.__lt__", "syft.lib.python.Bool"),
        ("syft.lib.python.Set.__ne__", "syft.lib.python.Bool"),
        ("syft.lib.python.Set.__or__", "syft.lib.python.Set"),
        ("syft.lib.python.Set.__sub__", "syft.lib.python.Set"),
        ("syft.lib.python.Set.__xor__", "syft.lib.python.Set"),
        ("syft.lib.python.Set.add", "syft.lib.python._SyNone"),
        ("syft.lib.python.Set.clear", "syft.lib.python._SyNone"),
        ("syft.lib.python.Set.difference", "syft.lib.python.Set"),
        ("syft.lib.python.Set.difference_update", "syft.lib.python._SyNone"),
        ("syft.lib.python.Set.discard", "syft.lib.python._SyNone"),
        ("syft.lib.python.Set.intersection", "syft.lib.python.Set"),
        ("syft.lib.python.Set.intersection_update", "syft.lib.python._SyNone"),
        ("syft.lib.python.Set.isdisjoint", "syft.lib.python.Bool"),
        ("syft.lib.python.Set.issuperset", "syft.lib.python.Bool"),
        ("syft.lib.python.Set.pop", "syft.lib.python._SyNone"),
        ("syft.lib.python.Set.remove", "syft.lib.python._SyNone"),
        (
            "syft.lib.python.Set.symmetric_difference_update",
            "syft.lib.python._SyNone",
        ),
        ("syft.lib.python.Set.symmetric_difference", "syft.lib.python.Set"),
        ("syft.lib.python.Set.union", "syft.lib.python.Set"),
        ("syft.lib.python.Set.update", "syft.lib.python._SyNone"),
        (
            "syft.lib.python.collections.SyOrderedDict.__contains__",
            "syft.lib.python.Bool",
        ),
        (
            "syft.lib.python.collections.SyOrderedDict.__delitem__",
            "syft.lib.python._SyNone",
        ),
        (
            "syft.lib.python.collections.SyOrderedDict.__eq__",
            "syft.lib.python.Bool",
        ),
        (
            "syft.lib.python.collections.SyOrderedDict.__ge__",
            "syft.lib.python.Bool",
        ),
        (
            "syft.lib.python.collections.SyOrderedDict.__getitem__",
            "syft.lib.python.Any",
        ),
        (
            "syft.lib.python.collections.SyOrderedDict.__gt__",
            "syft.lib.python.Bool",
        ),
        (
            "syft.lib.python.collections.SyOrderedDict.__le__",
            "syft.lib.python.Bool",
        ),
        (
            "syft.lib.python.collections.SyOrderedDict.__iter__",
            "syft.lib.python.Iterator",
        ),
        ("syft.lib.python.collections.SyOrderedDict.__len__", "syft.lib.python.Int"),
        (
            "syft.lib.python.collections.SyOrderedDict.__lt__",
            "syft.lib.python.Bool",
        ),
        (
            "syft.lib.python.collections.SyOrderedDict.__ne__",
            "syft.lib.python.Bool",
        ),
        (
            "syft.lib.python.collections.SyOrderedDict.__setitem__",
            "syft.lib.python._SyNone",
        ),
        (
            "syft.lib.python.collections.SyOrderedDict.clear",
            "syft.lib.python._SyNone",
        ),
        (
            "syft.lib.python.collections.SyOrderedDict.copy",
            "syft.lib.python.collections.SyOrderedDict",
        ),
        (
            "syft.lib.python.collections.SyOrderedDict.fromkeys",
            "syft.lib.python.collections.SyOrderedDict",
        ),
        ("syft.lib.python.collections.SyOrderedDict.items", "syft.lib.python.Iterator"),
        ("syft.lib.python.collections.SyOrderedDict.keys", "syft.lib.python.Iterator"),
        (
            "syft.lib.python.collections.SyOrderedDict.move_to_end",
            "syft.lib.python._SyNone",
        ),
        ("syft.lib.python.collections.SyOrderedDict.pop", "syft.lib.python.Any"),
        ("syft.lib.python.collections.SyOrderedDict.popitem", "syft.lib.python.Any"),
        (
            "syft.lib.python.collections.SyOrderedDict.setdefault",
            "syft.lib.python.Any",
        ),
        (
            "syft.lib.python.collections.SyOrderedDict.update",
            "syft.lib.python._SyNone",
        ),
        (
            "syft.lib.python.collections.SyOrderedDict.values",
            "syft.lib.python.Iterator",
        ),
        ("syft.lib.python.collections.SyOrderedDict.items", "syft.lib.python.List"),
        (
            "syft.lib.python.collections.SyOrderedDict.dict_get",
            "syft.lib.python.Any",
        ),
    ]

    dynamic_objects = [("syft.lib.python.Bool.my_field", "syft.lib.python.Int")]

    add_modules(ast, modules)
    add_classes(ast, classes)
    add_methods(ast, methods)
    add_dynamic_objects(ast, dynamic_objects)

    for klass in ast.classes:
        klass.create_pointer_class()
        klass.create_send_method()
        klass.create_storable_object_attr_convenience_methods()

    return ast
