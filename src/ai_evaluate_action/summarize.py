import json
from pathlib import Path
from statistics import mean
from typing import Any, NamedTuple, TypeAlias, TypedDict

from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel


class Results(BaseModel):
    rows: list[dict[str, Any]]
    metrics: dict[str, float]
    studio_url: str | None = None


EvaluatorName: TypeAlias = str
Category: TypeAlias = str
ValueName: TypeAlias = str


class ParsedRow(TypedDict):
    inputs: dict[str, str]
    outputs: dict[EvaluatorName, dict[ValueName, Any]]


class ParsedResults(Results):
    rows: list[ParsedRow]


def template_parameters(parsed_results: ParsedResults) -> dict[str, Any]:
    class SystemPrompt(NamedTuple):
        name: str
        value: str

    class ExtraRow(ParsedRow):
        system_prompt: SystemPrompt
        eval_scores: dict[str, float | int]

    tests: dict[tuple[str, str], list[ExtraRow]] = {}
    system_prompts: set[SystemPrompt] = set()
    for row in parsed_results.rows:
        description = json.loads(row["inputs"]["description"])
        system_prompt = SystemPrompt(name=description["context"]["system-prompt"], value=row["inputs"]["context"])

        eval_scores = {
            evaluator_name: next(score for score in outputs.values() if isinstance(score, (float, int)))
            for evaluator_name, outputs in row["outputs"].items()
        }

        tests.setdefault(
            (row["inputs"]["query"], row["inputs"]["ground_truth"]),
            [],
        ).append(ExtraRow(**row, system_prompt=system_prompt, eval_scores=eval_scores))

        system_prompts.add(system_prompt)

    aggregated_eval_scores: dict[str, dict[str, list[int | float]]] = {}

    for rows in tests.values():
        for row in rows:
            for evaluator_name in row["outputs"]:
                aggregated_eval_scores.setdefault(row["system_prompt"].name, {}).setdefault(evaluator_name, []).append(
                    row["eval_scores"][evaluator_name]
                )

    return {
        "system_prompts": system_prompts,
        "tests": tests,
        "average_eval_scores": {
            system_prompt: {evaluator_name: mean(v) for evaluator_name, v in evaluator_scores.items()}
            for system_prompt, evaluator_scores in aggregated_eval_scores.items()
        },
        "evaluator_names": list(parsed_results.rows[0]["outputs"].keys()),
    }


def summarize_results(results: dict, summary_path: Path, *, show_raw_output: bool = True) -> None:
    def parse_row(row: dict[str, Any]) -> ParsedRow:
        inputs = {k.removeprefix("inputs."): (v) for k, v in row.items() if k.startswith("inputs.")}
        outputs: dict[EvaluatorName, dict[ValueName, Any]] = {}

        for k, v in {k: v for k, v in row.items() if k.startswith("outputs.")}.items():
            _, evaluator_name, value_name = k.split(".")

            evaluator_dict = outputs.setdefault(evaluator_name, {})
            evaluator_dict[value_name] = v

        return {"inputs": inputs, "outputs": outputs}

    results_model = Results.model_validate(results)

    parsed_results = ParsedResults(
        rows=list(map(parse_row, results_model.rows)),
        metrics=results_model.metrics,
        studio_url=results_model.studio_url,
    )

    env = Environment(loader=FileSystemLoader(Path(__file__).parent.resolve()))
    template = env.get_template("summary.md.jinja")

    summary_path.write_text(
        template.render(**template_parameters(parsed_results), show_raw_output=show_raw_output), encoding="utf-8"
    )


if __name__ == "__main__":
    import json

    with Path(__file__, "..", "results.jsonl").resolve().open() as f:
        results = json.load(f)

    summarize_results(results, Path(__file__, "..", "summary.md").resolve())
