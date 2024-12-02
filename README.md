# Azure AI Evaluation GitHub Action

This GitHub Action enables offline evaluation of AI models within your CI/CD pipelines. It is designed to streamline the evaluation process, allowing you to assess model performance and make informed decisions before deploying to production. 

Offline evaluation involves testing AI models using test datasets to measure their performance on various quality and safety metrics such as fluency, coherence and content safety. After selecting a model in the [Azure AI Model Catalog](https://azure.microsoft.com/en-us/products/ai-model-catalog?msockid=1f44c87dd9fa6d1e257fdd6dd8406c42) or [GitHub Model marketplace](https://github.com/marketplace/models), offline pre-production evaluation is crucial for AI application validation during integration testing, allowing developers to identify potential issues and make improvements before deploying the model or application to production (e.g., when updating system meta prompts). 

## Features
* **Automated Evaluation:** Integrate offline evaluation into your CI/CD workflows to automate the pre-production assessment of AI models. 
* **Out of the Box and Custom Evaluators:** Leverage existing evaluators provided by the [Azure AI Evaluation SDK](https://learn.microsoft.com/en-us/azure/ai-studio/how-to/develop/evaluate-sdk) or add your own custom evaluators. The following evaluators are supported: 
  * BleuScoreEvaluator
  * CoherenceEvaluator 
  * ContentSafetyEvaluator 
  * HateUnfairnessEvaluator 
  * SelfHarmEvaluator 
  * SexualEvaluator 
  * ViolenceEvaluator 
  * F1ScoreEvaluator 
  * FluencyEvaluator 
  * GleuScoreEvaluator 
  * GroundednessEvaluator 
  * MeteorScoreEvaluator 
  * ProtectedMaterialEvaluator 
  * QAEvaluator 
  * RelevanceEvaluator 
  * RetrievalEvaluator 
  * RougeScoreEvaluator 
  * SimilarityEvaluator 
  * IndirectAttackEvaluator 
* **Seamless Integration:** Easily integrate with existing GitHub workflows to run evaluation based on rules that you specify in your workflows (e.g., when changes are committed to feature flag configuration or system prompt files). 

## Pre-Requisites
To use the Azure AI Evaluation GitHub Action you need to first install the Azure AI evaluation SDK by following the instructions [here](https://learn.microsoft.com/en-us/azure/ai-studio/how-to/develop/evaluate-sdk#getting-started). 

## Usage
To use this GitHub Action, add this GitHub Action to your CI/CD workflows and specify the trigger criteria (e.g., on commit) and file paths to trigger your automated workflows (note: to minimize costs you should avoid running evaluation on every commit). This example illustrates how Azure AI Evaluation can be run when changes are committed to specific files in your repo (please update GENAI_EVALS_DATA_PATH to point to the correct directory in your repo):

```
name: Sample Evaluate Action
on:
  workflow_call:
  workflow_dispatch:

permissions:
  id-token: write
  contents: read

jobs:
  evaluate:
    runs-on: ubuntu-latest
    env:
      GENAI_EVALS_CONFIG_PATH: ${{ github.workspace }}/evaluate-config.json
      GENAI_EVALS_DATA_PATH: ${{ github.workspace }}/.github/.test_files/eval-input.jsonl
    steps:
      - uses: actions/checkout@v4
      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.OIDC_AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.OIDC_AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.OIDC_AZURE_SUBSCRIPTION_ID }}
      - name: Write evaluate config
        run: |
          cat > ${{ env.GENAI_EVALS_CONFIG_PATH }} <<EOF
          {
            "data": "${{ env.GENAI_EVALS_DATA_PATH }}",
            "evaluators": {
              "coherence": "CoherenceEvaluator",
              "fluency": "FluencyEvaluator"
            },
            "ai_model_configuration": {
              "type": "azure_openai",
              "azure_endpoint": "${{ secrets.AZURE_OPENAI_ENDPOINT }}",
              "azure_deployment": "${{ secrets.AZURE_OPENAI_CHAT_DEPLOYMENT }}",
              "api_key": "${{ secrets.AZURE_OPENAI_API_KEY }}",
              "api_version": "${{ secrets.AZURE_OPENAI_API_VERSION }}"
            }
          }
          EOF
      - name: Run AI Evaluation
        id: run-ai-evaluation
        uses: microsoft/genai-evals@main
        with:
          evaluate-configuration: ${{ env.GENAI_EVALS_CONFIG_PATH }}
```
## Outputs
Evaluation results will be output to the summary section for each AI Evaluation GitHub Action run under Actions in GitHub.com.

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
