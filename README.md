# Gemini JSON OCR

Gemini JSON OCR is a **proof of concept** showing how easy it is to use
[the latest Google Gemini](https://blog.google/technology/google-deepmind/google-gemini-ai-update-december-2024/)
to extract structured JSONs from documents.

## Usage

```zsh
$ export GOOGLE_API_KEY=<get your API key at https://aistudio.google.com/app/apikey>
$ uv run scan.py /Users/maurycy/Desktop/test
INFO:root:Processing file: MX-C304W_16122024_143019.pdf
Results for MX-C304W_16122024_143019.pdf have been written to /Users/maurycy/Desktop/test/MX-C304W_16122024_143019.pdf.json
```

Resulting in a JSON, such as:

```json
{
  "waybill": {
    "scac": "SEAU",
    "booking_no": "4803804131",
    "bl_no": "4803804131",
    "vessel": "MERIDIAN",
    "containers": [ "TLLU5242619", "MSKU829454" ]
  }
}
```

## Getting Started

Make sure that you've got [uv](https://docs.astral.sh/uv/)
[installed](https://docs.astral.sh/uv/getting-started/installation/):

```zsh
# macOS
brew install uv
# macOS or Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

(No need to install Python etc. `uv` will take care of that!)

## Advanced usage

The prompt is in the `prompt.txt`.

Supported environment variables:

- `GEMINI_MODEL`, by default `gemini-2.0-flash-exp`
- `GOOGLE_API_KEY`, to be retrieved from [Google AI Studio](https://aistudio.google.com/app/apikey)
