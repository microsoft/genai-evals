import argparse
import os
from pathlib import Path

from azure.ai.evaluation import RougeType, evaluate
from azure.identity import DefaultAzureCredential

from ai_evaluate_action.config import Config
from ai_evaluate_action.summarize import summarize_results


def main(*, config_path: str | os.PathLike[str] | Path, summary_path: str | os.PathLike[str] | Path | None) -> None:
    config_path = Path(config_path).resolve()
    summary_path = Path(summary_path).resolve() if summary_path is not None else None

    config = Config.model_validate_json(config_path.read_text(encoding="utf-8"))

    data_path = config.data if config.data.is_absolute() else Path(config_path.parent, config.data)

    output_path = (
        config.output_path
        if config.output_path is None
        else str(
            config.output_path if config.output_path.is_absolute() else Path(config_path.parent, config.output_path)
        )
    )

    results = evaluate(
        data=str(data_path),
        evaluators=config.hydrate_evaluators(
            azure_ai_project=config.azure_ai_project,
            credential=DefaultAzureCredential(),
            model_config=config.ai_model_configuration,
            rouge_type=RougeType.ROUGE_L,  # TODO: Need a better configuration story for individual evaluators
        ),
        evaluation_name=config.evaluation_name,
        target=None,
        evaluator_config=config.evaluator_config,
        output_path=output_path,
    )

    if summary_path is not None:
        summarize_results(results, summary_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", dest="config_path", required=True)
    parser.add_argument("--summary", dest="summary_path", required=False)
    main(**vars(parser.parse_args()))
