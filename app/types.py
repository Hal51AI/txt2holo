from typing import TypedDict, Literal, Union

Numeric = Union[int, float]


class StabilityAPIArtifacts(TypedDict):
    base64: str
    seed: int
    finishedReason: Literal["SUCCESS", "CONTENT_FILTERED", "ERROR"]


class StabilityAPIResponse(TypedDict):
    artifacts: list[StabilityAPIArtifacts]
