import inspect
from pathlib import Path
from typing import Callable, Literal, Type, TypeAlias, TypeVar

from azure.ai.evaluation import (
    AzureAIProject,
    AzureOpenAIModelConfiguration,
    BleuScoreEvaluator,
    CoherenceEvaluator,
    ContentSafetyEvaluator,
    EvaluatorConfig,
    F1ScoreEvaluator,
    FluencyEvaluator,
    GleuScoreEvaluator,
    GroundednessEvaluator,
    HateUnfairnessEvaluator,
    IndirectAttackEvaluator,
    MeteorScoreEvaluator,
    OpenAIModelConfiguration,
    ProtectedMaterialEvaluator,
    QAEvaluator,
    RelevanceEvaluator,
    RetrievalEvaluator,
    RougeScoreEvaluator,
    SelfHarmEvaluator,
    SexualEvaluator,
    SimilarityEvaluator,
    ViolenceEvaluator,
)
from pydantic import BaseModel

EvaluatorName: TypeAlias = Literal[
    "BleuScoreEvaluator",
    "CoherenceEvaluator",
    "ContentSafetyEvaluator",
    "HateUnfairnessEvaluator",
    "SelfHarmEvaluator",
    "SexualEvaluator",
    "ViolenceEvaluator",
    "F1ScoreEvaluator",
    "FluencyEvaluator",
    "GleuScoreEvaluator",
    "GroundednessEvaluator",
    "MeteorScoreEvaluator",
    "ProtectedMaterialEvaluator",
    "QAEvaluator",
    "RelevanceEvaluator",
    "RetrievalEvaluator",
    "RougeScoreEvaluator",
    "SimilarityEvaluator",
    "IndirectAttackEvaluator",
]

T = TypeVar("T")

EVALUATORS: dict[EvaluatorName, Type[Callable]] = {
    "BleuScoreEvaluator": BleuScoreEvaluator,
    "CoherenceEvaluator": CoherenceEvaluator,
    "ContentSafetyEvaluator": ContentSafetyEvaluator,
    "HateUnfairnessEvaluator": HateUnfairnessEvaluator,
    "SelfHarmEvaluator": SelfHarmEvaluator,
    "SexualEvaluator": SexualEvaluator,
    "ViolenceEvaluator": ViolenceEvaluator,
    "F1ScoreEvaluator": F1ScoreEvaluator,
    "FluencyEvaluator": FluencyEvaluator,
    "GleuScoreEvaluator": GleuScoreEvaluator,
    "GroundednessEvaluator": GroundednessEvaluator,
    "MeteorScoreEvaluator": MeteorScoreEvaluator,
    "ProtectedMaterialEvaluator": ProtectedMaterialEvaluator,
    "QAEvaluator": QAEvaluator,
    "RelevanceEvaluator": RelevanceEvaluator,
    "RetrievalEvaluator": RetrievalEvaluator,
    "RougeScoreEvaluator": RougeScoreEvaluator,
    "SimilarityEvaluator": SimilarityEvaluator,
    "IndirectAttackEvaluator": IndirectAttackEvaluator,
}


class EvaluateConfig(BaseModel):
    data: Path
    ai_model_configuration: AzureOpenAIModelConfiguration | OpenAIModelConfiguration
    evaluators: dict[str, EvaluatorName]
    evaluation_name: str | None = None
    evaluator_config: dict[str, EvaluatorConfig] | None = None
    azure_ai_project: AzureAIProject | None = None

    def hydrate_evaluators(self, **kwargs: object) -> dict[str, Callable]:
        def initialize_evaluator(evaluator_class: Type[T]) -> T:
            init_signature = inspect.signature(evaluator_class.__init__)
            required = {
                k
                for k, v in init_signature.parameters.items()
                if (v.kind is v.POSITIONAL_OR_KEYWORD and k != "self" and v.default is v.empty)
            }

            parameters = {k: kwargs[k] for k in kwargs for k in required}

            return evaluator_class(**parameters)

        return {
            evaluator_name: initialize_evaluator(EVALUATORS[evaluator_classname])
            for evaluator_name, evaluator_classname in self.evaluators.items()
        }


class ActionConfig(BaseModel):
    output_path: Path | None = None
    show_raw_output: bool = True
