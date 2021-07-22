# future
from __future__ import annotations

# third party
import numpy as np
import torch as th

# relative
# syft relative
from ...core.common.serde.recursive import RecursiveSerde
from ..common.serde.serializable import bind_protobuf
from .ancestors import AutogradTensorAncestor
from .ancestors import PhiTensorAncestor
from .passthrough import PassthroughTensor


@bind_protobuf
class Tensor(
    PassthroughTensor, AutogradTensorAncestor, PhiTensorAncestor, RecursiveSerde
):

    __attr_allowlist__ = ['child']

    def __init__(self, child):
        """data must be a list of numpy array"""

        if isinstance(child, list):
            child = np.array(child)

        if isinstance(child, th.Tensor):
            child = child.numpy()

        if not isinstance(child, PassthroughTensor) and not isinstance(
            child, np.ndarray
        ):
            raise Exception("Data must be list or nd.array")

        super().__init__(child=child)

