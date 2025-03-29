from enum import Enum
from smolagents import HfApiModel, LiteLLMModel


class ModelType(Enum):
    HFAPI = 0
    LITELLM = 1


class ModelFactory:
    def __init__(self, type: str, model_id: str, api_key: str, api_base: str):
        self.type = ModelType[type.upper()]
        self.model_id = model_id
        self.api_key = api_key
        self.api_base = api_base

    def __call__(self):
        match self.type:
            case ModelType.HFAPI:
                return HfApiModel(model_id=self.model_id, token=self.api_key)
            case ModelType.LITELLM:
                return LiteLLMModel(
                    model_id=self.model_id,
                    api_key=self.api_key,
                    api_base=self.api_base,
                )
