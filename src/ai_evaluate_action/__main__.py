import argparse
import os
from pathlib import Path

from azure.ai.evaluation import RougeType, evaluate
from azure.identity import DefaultAzureCredential

from ai_evaluate_action.config import ActionConfig, EvaluateConfig
from ai_evaluate_action.summarize import summarize_results


def main(
    *,
    action_config_path: str | os.PathLike[str] | Path,
    evaluate_config_path: str | os.PathLike[str] | Path,
    summary_path: str | os.PathLike[str] | Path | None,
) -> None:
    action_config_path = Path(action_config_path).resolve()
    evaluate_config_path = Path(evaluate_config_path).resolve()
    summary_path = Path(summary_path).resolve() if summary_path is not None else None

    action_config = ActionConfig.model_validate_json(action_config_path.read_text(encoding="utf-8"))
    evaluate_config = EvaluateConfig.model_validate_json(evaluate_config_path.read_text(encoding="utf-8"))

    data_path = (
        evaluate_config.data
        if evaluate_config.data.is_absolute()
        else Path(action_config_path.parent, evaluate_config.data)
    )

    output_path = (
        action_config.output_path
        if action_config.output_path is None
        else str(
            action_config.output_path
            if action_config.output_path.is_absolute()
            else Path(action_config_path.parent, action_config.output_path)
        )
    )

    results = evaluate(
        data=str(data_path),
        evaluators=evaluate_config.hydrate_evaluators(
            azure_ai_project=evaluate_config.azure_ai_project,
            credential=DefaultAzureCredential(),
            model_config=evaluate_config.ai_model_configuration,
            rouge_type=RougeType.ROUGE_L,  # TODO: Need a better configuration story for individual evaluators
        ),
        evaluation_name=evaluate_config.evaluation_name,
        target=None,
        evaluator_config=evaluate_config.evaluator_config,
        output_path=output_path,
    )

    if summary_path is not None:
        summarize_results(results, summary_path, show_raw_output=action_config.show_raw_output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--action-config", dest="action_config_path", required=True)
    parser.add_argument("--evaluate-config", dest="evaluate_config_path", required=True)
    parser.add_argument("--summary", dest="summary_path", required=False)
    main(**vars(parser.parse_args()))
