# stdlib
import io
import json
from typing import Iterator
from typing import Optional

# third party
import docker
from typing_extensions import Self

# relative
from ...custom_worker.config import DockerWorkerConfig
from ...custom_worker.config import WorkerConfig
from ...node.credentials import SyftVerifyKey
from ...serde.serializable import serializable
from ...types.base import SyftBaseModel
from ...types.datetime import DateTime
from ...types.syft_object import SYFT_OBJECT_VERSION_1
from ...types.syft_object import SyftObject
from ...types.uid import UID
from ..response import SyftError
from ..response import SyftSuccess


def parse_output(log_iterator: Iterator) -> str:
    log = ""
    for line in log_iterator:
        for item in line.values():
            if isinstance(item, str):
                log += item
            elif isinstance(item, dict):
                log += json.dumps(item)
            else:
                log += str(item)
    return log


@serializable()
class ContainerImageRegistry(SyftBaseModel):
    url: str
    tls_enabled: bool

    __repr_attrs__ = ["url"]

    @classmethod
    def from_url(cls, full_str: str):
        return cls(url=full_str, tls_enabled=full_str.startswith("https"))

    def __hash__(self) -> int:
        return hash(self.url + str(self.tls_enabled))

    def __str__(self) -> str:
        return self.url


@serializable()
class SyftWorkerImageIdentifier(SyftBaseModel):
    """
    Class to identify syft worker images.
    If a user provides an image's identifier with
    "docker.io/openmined/test-nginx:0.7.8", the convention we use for
    image name, tag and repo for now is
        tag = 0.7.8
        repo = openmined/test-nginx
        repo_with_tag = openmined/test-nginx:0.7.8
        full_name = docker.io/openmined/test-nginx
        full_name_with_tag = docker.io/openmined/test-nginx:0.7.8

    References:
        https://docs.docker.com/engine/reference/commandline/tag/#tag-an-image-referenced-by-name-and-tag
    """

    registry: Optional[ContainerImageRegistry]
    repo: str
    tag: str

    __repr_attrs__ = ["registry", "repo", "tag"]

    @classmethod
    def from_str(cls, full_str: str) -> Self:
        repo_url, tag = full_str.rsplit(":", 1)
        args = repo_url.rsplit("/", 2)
        if len(args) == 3:
            registry = ContainerImageRegistry.from_url(args[0])
            repo = "/".join(args[1:])
        else:
            registry = None
            repo = "/".join(args)
        return cls(repo=repo, registry=registry, tag=tag)

    @property
    def repo_with_tag(self) -> str:
        return f"{self.repo}:{self.tag}"

    @property
    def full_name_with_tag(self) -> str:
        if self.registry:
            return f"{self.registry.url}/{self.repo}:{self.tag}"
        else:
            # default registry is always docker.io
            return f"docker.io/{self.repo}:{self.tag}"

    def __hash__(self) -> int:
        return hash(self.repo + self.tag + str(hash(self.registry)))

    def __str__(self) -> str:
        return f"registry: {str(self.registry)}, repo: {self.repo}, tag: {self.tag}"


@serializable()
class SyftWorkerImage(SyftObject):
    __canonical_name__ = "SyftWorkerImage"
    __version__ = SYFT_OBJECT_VERSION_1

    # __attr_unique__ = ["config"]
    __attr_searchable__ = ["config", "image_hash", "created_by"]
    __repr_attrs__ = ["image_identifier", "image_hash", "created_at"]

    id: UID
    config: Optional[WorkerConfig]
    image_identifier: Optional[SyftWorkerImageIdentifier]
    image_hash: Optional[str]
    created_at: DateTime = DateTime.now()
    created_by: SyftVerifyKey


def build_using_docker(
    client: docker.DockerClient,
    worker_image: SyftWorkerImage,
    push: bool = True,
    dev_mode: bool = False,
):
    if not isinstance(worker_image.config, DockerWorkerConfig):
        # Handle this to worker with CustomWorkerConfig later
        return SyftError("We only support DockerWorkerConfig")

    try:
        file_obj = io.BytesIO(worker_image.config.dockerfile.encode("utf-8"))

        # docker build -f <dockerfile> <buildargs> <path>

        # Enable this once we're able to copy worker_cpu.dockerfile in backend
        # buildargs = {"SYFT_VERSION_TAG": "local-dev"} if dev_mode else {}
        result = client.images.build(
            fileobj=file_obj,
            rm=True,
            tag=worker_image.image_identifier.repo_with_tag,
            forcerm=True,
        )
        worker_image.image_hash = result[0].id
        log = parse_output(result[1])
        return worker_image, SyftSuccess(
            message=f"Build {worker_image} succeeded.\n{log}"
        )
    except docker.errors.BuildError as e:
        return worker_image, SyftError(message=f"Failed to build {worker_image}. {e}")
