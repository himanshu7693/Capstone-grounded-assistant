# Guardrailed AI Assistant

## Task

Build an assistant that stays inside its remit and can be evaluated.

This project implements a small technical study assistant whose remit is Python, Generative AI, LLMs, prompt engineering, machine learning fundamentals, RAG, embeddings, APIs, and related software-development concepts.

## Requirements covered

### 1. Guardrails on off-topic and unsafe requests

The application performs deterministic checks **before** calling the model.

- Unsafe patterns are rejected immediately.
- Known off-topic patterns are rejected immediately.
- Requests without relevant technical-topic signals are treated as off-topic.
- The LLM also receives a system instruction reinforcing the same remit and safety boundary.

Rejected requests therefore do not consume model tokens in the normal path.

### 2. Evaluation set with scored results

`evaluation_set.json` contains 13 fixed test cases:

- 5 in-scope questions
- 4 off-topic questions
- 4 unsafe questions

`evaluate.py` runs all cases and reports:

- pass/fail for every case
- total score
- expected vs. actual decision

### 3. Cost/token usage measured

For allowed LLM calls, the program reads token counts from Gemini's response usage metadata:

- input/prompt tokens
- output/candidate tokens

It then calculates an estimated cost using configurable per-million-token prices.

By default the prices are `0`, representing a free/quota-based run. To model a paid plan, set:

```bash
export GEMINI_INPUT_PRICE_PER_MILLION="YOUR_PRICE"
export GEMINI_OUTPUT_PRICE_PER_MILLION="YOUR_PRICE"
```

The evaluation report includes total measured tokens and estimated cost.

## Project structure

```text
guardrail-assistant/
├── app.py
├── evaluate.py
├── evaluation_set.json
├── requirements.txt
└── README.md
```

## Architecture

```text
User request
     |
     v
Deterministic guardrails
     |
     +---- unsafe ------> Refuse
     |
     +---- off-topic ---> Refuse
     |
     v
Gemini assistant
     |
     v
Answer + token usage
     |
     v
Cost estimate
```

## Setup

Python 3.10+ is recommended.

Install dependencies:

```bash
pip install -r requirements.txt
```

Set a Gemini API key:

### Linux/macOS

```bash
export GEMINI_API_KEY="your_api_key_here"
```

### Windows PowerShell

```powershell
$env:GEMINI_API_KEY="your_api_key_here"
```

## Run the assistant

```bash
python app.py
```

Example:

```text
Ask the assistant: What is RAG?

Decision: allowed
Answer: RAG combines retrieval of relevant external context with generation...
Input tokens: 80
Output tokens: 60
Estimated cost: $0.000000
```

## Run the evaluation

```bash
python evaluate.py
```

Example report:

```text
Evaluation results
============================================================
PASS E01 | expected=allowed    | actual=allowed
PASS E02 | expected=allowed    | actual=allowed
...
PASS E13 | expected=unsafe     | actual=unsafe
============================================================
Passed: 13/13
Score: 100.0%
Input tokens measured: 4xx
Output tokens measured: 2xx
Estimated API cost: $0.000000
```

Exact token counts and model wording vary between runs.

## Design decisions

The project deliberately uses simple deterministic guardrails rather than a large moderation framework. This makes the boundary easy to inspect and evaluate.

The evaluation set is fixed so the same tests can be run after future changes. A score is calculated from whether the assistant's decision matches the expected behavior.

The token/cost measurement is kept separate from the guardrail decision. This makes it visible that blocked requests can be handled without an LLM call, while allowed requests consume measurable tokens.

## Limitations

This is a small educational guardrail demonstration, not a production safety system. Keyword-based detection can miss paraphrases and can also produce false positives. A production system should use stronger policy enforcement and safety classifiers in addition to application-level rules.

## Security note

Never commit `GEMINI_API_KEY` or other secrets to GitHub.
