# Mistral La Plateforme Provider

## Usage Example

```
gptscript --default-model='mistral-large-latest from github.com/gptscript-ai/mistral-laplateforme-provider' examples/helloworld.gpt
```


## Development

* You need an MISTRAL_API_KEY set in your environment.

```
export MISTRAL_API_KEY=<your-api-key>
```

Run using the following commands

```
python -m venv .venv
source ./.venv/bin/activate
pip install --upgrade -r requirements.txt
# Optional - prints more debugging and output from provider
export GPTSCRIPT_DEBUG=true
./run.sh
```

```
gptscript --default-model="mistral-large-latest from http://127.0.0.1:8000/v1" examples/bob.gpt
```
