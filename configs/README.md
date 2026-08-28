# Configuration templates

All model calls use an OpenAI-compatible chat-completion interface. Store the 12 tested target models under `configs/llm/` and all other supporting models under `configs/auxiliary_llm/`. Copy `configs/llm/example.yaml`, place the renamed copy in the appropriate directory, and use this format:

```yaml
llm_type: "OpenAiChatLLM"
base_url: "https://your-provider.example/v1"
api_key_env: "YOUR_PROVIDER_API_KEY"
model_name: "your-model-name"
temperature: 0.2
```

Set `base_url` to the compatible endpoint supplied by your provider and export the variable named by `api_key_env` in your local shell. `api_key_env` stores only the variable name, never the key itself. Never add an `api_key` value containing a real credential to a tracked file.

The bundled `example.yaml` is documentation only and is automatically excluded from `--all-target-models`. `configs/auxiliary_llm/gpt-5.4.yaml` supports scenario generation, tool construction, the adaptive attacker, and the main judge. `configs/auxiliary_llm/claude-opus-4-7.yaml` supports candidate-scenario quality filtering. GPT-4o and Llama-4 under `configs/auxiliary_llm/`, together with the target-model configuration `configs/llm/deepseek-v3.2.yaml`, support multi-judge validation. Provider-specific model IDs may change; use the identifier documented by the endpoint you access.
