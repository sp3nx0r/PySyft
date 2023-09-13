# stdlib
from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional
from typing import Type
from typing import Union

# relative
from ..util.autoreload import autoreload_enabled
from .syft_object import Context
from .syft_object import SYFT_OBJECT_VERSION_1
from .syft_object import SyftBaseObject
from .syft_object import SyftObject
from .transforms import generate_transform_wrapper
from .transforms import validate_klass_and_version


class SyftMigrationRegistry:
    __migration_version_registry__: Dict[str, Dict[int, str]] = {}
    __migration_transform_registry__: Dict[str, Dict[str, Callable]] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        klass = type(cls) if not isinstance(cls, type) else cls

        if hasattr(klass, "__canonical_name__") and hasattr(klass, "__version__"):
            mapping_string = klass.__canonical_name__
            klass_version = cls.__version__
            fqn = f"{cls.__module__}.{cls.__name__}"

            if (
                mapping_string in cls.__migration_version_registry__
                and not autoreload_enabled()
            ):
                versions = cls.__migration_version_registry__[mapping_string]
                versions[klass_version] = fqn
            else:
                # only if the cls has not been registered do we want to register it
                cls.__migration_version_registry__[mapping_string] = {
                    klass_version: fqn
                }

    @classmethod
    def register_transform(
        cls, klass_type_str: str, version_from: int, version_to: int, method: Callable
    ) -> None:
        if klass_type_str not in cls.__migration_version_registry__:
            raise Exception(f"{klass_type_str} is not yet registered.")

        available_versions = cls.__migration_version_registry__[klass_type_str]

        versions_exists = (
            version_from in available_versions and version_to in available_versions
        )

        if versions_exists:
            mapping_string = f"{version_from}x{version_to}"
            if klass_type_str not in cls.__migration_transform_registry__:
                cls.__migration_transform_registry__[klass_type_str] = {}
            cls.__migration_transform_registry__[klass_type_str][
                mapping_string
            ] = method
        else:
            raise Exception(
                f"Available versions for {klass_type_str} are: {available_versions}."
                f"You're trying to add a transform from version: {version_from} to version: {version_to}"
            )

    @classmethod
    def get_migration(
        cls, type_from: Type[SyftObject], type_to: Type[SyftObject]
    ) -> Callable:
        for type_from_mro in type_from.mro():
            if issubclass(type_from_mro, SyftBaseObject):
                klass_from = type_from_mro.__canonical_name__
                version_from = type_from_mro.__version__

                for type_to_mro in type_to.mro():
                    if issubclass(type_to_mro, SyftBaseObject):
                        klass_to = type_to_mro.__canonical_name__
                        version_to = type_to_mro.__version__

                    if klass_from == klass_to:
                        mapping_string = f"{version_from}x{version_to}"
                        if (
                            mapping_string
                            in cls.__migration_transform_registry__[klass_from]
                        ):
                            return cls.__migration_transform_registry__[klass_from][
                                mapping_string
                            ]

        raise Exception(
            f"No migration found for: {type_from} to {type_to} in the migration registry."
        )


def migrate(
    klass_from: Union[type, str],
    klass_to: Union[type, str],
    version_from: Optional[int] = None,
    version_to: Optional[int] = None,
) -> Callable:
    (
        klass_from_str,
        version_from,
        klass_to_str,
        version_to,
    ) = validate_klass_and_version(
        klass_from=klass_from,
        version_from=version_from,
        klass_to=klass_to,
        version_to=version_to,
    )

    if klass_from_str != klass_to_str:
        raise Exception(
            "Migration can only be performed across classes with same canonical name."
            f"Provided args: klass_from: {klass_from_str}, klass_to: {klass_to_str}"
        )

    if version_from is None or version_to is None:
        raise Exception(
            "Version information missing at either of the classes."
            f"{klass_from_str} has version: {version_from}, {klass_to_str} has version: {version_to}"
        )

    def decorator(function: Callable):
        transforms = function()

        wrapper = generate_transform_wrapper(
            klass_from=klass_from, klass_to=klass_to, transforms=transforms
        )

        SyftMigrationRegistry.register_transform(
            klass_type_str=klass_from_str,
            version_from=version_from,
            version_to=version_to,
            method=wrapper,
        )

        return function

    return decorator


class SyftObjectTable(SyftObject, SyftMigrationRegistry):
    """Syft Object which are stored in DocumentStore."""

    __canonical_name__ = "SyftObjectTable"
    __version__ = SYFT_OBJECT_VERSION_1

    def migrate_to(self, projection: type, context: Optional[Context] = None) -> Any:
        migration_transform = SyftMigrationRegistry.get_migration(
            type(self), projection
        )
        return migration_transform(self, context)