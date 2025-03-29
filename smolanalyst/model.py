from enum import Enum
from typing import TypedDict
from smolagents import HfApiModel, LiteLLMModel


class ModelType(Enum):
    HFAPI = 0
    LITELLM = 1


class ModelConfig(TypedDict):
    type: ModelType
    model_id: str
    api_key: str
    api_base: str


def model_factory(config: ModelConfig):
    match config["type"]:
        case ModelType.HFAPI:
            return HfApiModel(model_id=config["model_id"], token=config["api_key"])
        case ModelType.LITELLM:
            return LiteLLMModel(
                model_id=config["model_id"],
                api_key=config["api_key"],
                api_base=config["api_base"],
            )
