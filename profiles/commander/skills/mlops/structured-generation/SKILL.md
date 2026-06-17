---
name: structured-generation
description: "Constrained/structured LLM generation with regex, grammars, JSON schemas, and Pydantic models. Covers Microsoft Guidance and Outlines frameworks — both provide guaranteed-valid structured output but with different backend support and specialization."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Prompt Engineering, Structured Output, Constrained Generation, JSON, Pydantic, Grammar, Regex, Local Models]
    related_skills: [vllm, llama-cpp, obliteratus]
---

# Structured Generation

Constrained LLM output generation that guarantees valid JSON/XML/regex/code without post-hoc validation. Two canonical frameworks: **Guidance** (Microsoft Research) and **Outlines** (dottxt.ai). Both filter tokens at generation time rather than retrying on invalid output.

## When to Use

Use when you need:
- Guaranteed valid JSON, XML, or code output
- Format enforcement (dates, emails, IDs, etc.)
- Regex-constrained generation
- Multi-step workflows with Pythonic control flow
- Pydantic model validation with type-safe outputs
- Zero-overhead structured generation (no retry loops)

## Choosing between Guidance and Outlines

| Feature | Guidance | Outlines |
|---------|----------|----------|
| Regex constraints | ✅ | ✅ |
| Grammar/CFG support | ✅ | ✅ |
| Pydantic validation | ❌ | ✅ (native) |
| Token healing | ✅ | ❌ |
| Local models (Transformers, llama.cpp) | ✅ | ✅ |
| vLLM backend | ⚠️ indirect | ✅ (native) |
| Multi-step workflows | ✅ (Pythonic) | ⚠️ limited |
| JSON Schema | ⚠️ limited | ✅ |
| Learning curve | Low | Low |

**Choose Guidance** when you need token healing, multi-step workflows with context managers, or complex branching Python control flow.

**Choose Outlines** when you need Pydantic model support, maximum inference speed via FSM fast-forwarding, or native vLLM integration.

## Guidance — Constrained Generation (Microsoft Research)

**GitHub**: https://github.com/guidance-ai/guidance (18k+ stars)

### Installation

```bash
pip install guidance
pip install guidance[transformers]  # Hugging Face models
pip install guidance[llama_cpp]     # llama.cpp models
```

### Quick Start

```python
from guidance import models, gen

lm = models.OpenAI("gpt-4")

# Regex-constrained generation
result = lm + "Email: " + gen("email", regex=r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

# Selection constraint
from guidance import select
lm += "Sentiment: " + select(["positive", "negative", "neutral"], name="sentiment")
```

### Core Concepts

**Token Healing**: Guidance automatically backs up and regenerates when token boundaries would cause spacing issues.

**Context Managers**: Natural chat-style flow with `system()`, `user()`, `assistant()` blocks.

**Guidance Functions**: Reusable generation patterns with `@guidance` decorator.

```python
from guidance import guidance, gen, models

@guidance
def generate_person(lm):
    lm += "Name: " + gen("name", max_tokens=20, stop="\n")
    lm += "\nAge: " + gen("age", regex=r"[0-9]+", max_tokens=3)
    return lm

lm = models.Anthropic("claude-sonnet-4-5-20250929")
lm = generate_person(lm)
```

### With llama.cpp Backend

```python
from guidance.models import LlamaCpp

lm = LlamaCpp(
    model_path="/path/to/model.gguf",
    n_ctx=4096,
    n_gpu_layers=35
)

result = lm + "The capital of France is " + gen("capital", max_tokens=5)
```

### Key Patterns

```python
# JSON generation with regex constraints
lm += '{\n  "name": "' + gen("name", regex=r'[A-Za-z ]+', max_tokens=30) + '",\n  "age": "' + gen("age", regex=r"[0-9]+", max_tokens=3) + '"\n}'

# Multi-step ReAct agent
@guidance(stateless=False)
def react_agent(lm, question, tools, max_rounds=5):
    lm += f"Question: {question}\n\n"
    for i in range(max_rounds):
        lm += f"Thought {i+1}: " + gen("thought", stop="\n")
        lm += "\nAction: " + select(list(tools.keys()), name="action")
        tool_result = tools[lm["action"]]()
        lm += f"\nObservation: {tool_result}\n\n"
        lm += "Done? " + select(["Yes", "No"], name="done")
        if lm["done"] == "Yes":
            break
    lm += "\nFinal Answer: " + gen("answer", max_tokens=100)
    return lm
```

### Backend Configuration

```python
# OpenAI
from guidance import models
lm = models.OpenAI("gpt-4o-mini")

# Anthropic
lm = models.Anthropic("claude-sonnet-4-5-20250929")

# Transformers (Hugging Face)
from guidance.models import Transformers
lm = Transformers("microsoft/Phi-4-mini-instruct", device="cuda")

# llama.cpp
from guidance.models import LlamaCpp
lm = LlamaCpp(model_path="./model.Q4_K_M.gguf", n_gpu_layers=35)
```

### References

- `references/constraints.md` — Regex and grammar pattern library
- `references/backends.md` — Backend-specific configuration
- `references/examples.md` — Production-ready examples

---

## Outlines — Structured Text Generation (dottxt.ai)

**GitHub**: https://github.com/outlines-dev/outlines (8k+ stars)

### Installation

```bash
pip install outlines
pip install outlines[transformers]  # Hugging Face models
pip install outlines[llama_cpp]     # llama.cpp
pip install outlines[vllm]          # vLLM for production
```

### Quick Start

```python
import outlines

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")

# Choice generation
generator = outlines.generate.choice(model, ["positive", "negative", "neutral"])
sentiment = generator("This product is amazing!")

# Pydantic model generation
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
    email: str

generator = outlines.generate.json(model, User)
user = generator("Extract: John Doe, 30, john@example.com")
```

### Core Concepts

**FSM-based constrained sampling**: Outlines converts JSON Schema/Pydantic/regex to Finite State Machines that filter invalid tokens at generation time. Zero overhead — invalid tokens are never generated.

**Fast-forward optimization**: When only one token is valid, Outlines skips directly to it.

**Pydantic integration**: First-class support for type-safe output validation.

```python
from pydantic import BaseModel, Field
from enum import Enum

class Status(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Application(BaseModel):
    applicant: str
    status: Status
    priority: Literal["low", "medium", "high"]

generator = outlines.generate.json(model, Application)
result = generator("Generate application for Alice")
print(result.status)  # Status.PENDING (one of the enum values)
```

### Backend Configuration

```python
# Transformers (Hugging Face)
model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct", device="cuda")

# llama.cpp (GGUF)
model = outlines.models.llamacpp("./model.Q4_K_M.gguf", n_gpu_layers=35)

# vLLM (production throughput)
model = outlines.models.vllm("meta-llama/Llama-3.1-8B-Instruct", tensor_parallel_size=2)

# OpenAI (limited)
model = outlines.models.openai("gpt-4o-mini")
```

### Key Patterns

```python
# Regex generation
generator = outlines.generate.regex(model, r"[0-9]{3}-[0-9]{3}-[0-9]{4}")
phone = generator("Generate phone:")

# Integer/float generation
int_gen = outlines.generate.integer(model)
age = int_gen("Person's age:")

# Batch processing
def batch_extract(texts: list[str], schema: type[BaseModel]):
    model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")
    generator = outlines.generate.json(model, schema)
    return [generator(f"Extract from: {t}") for t in texts]
```

### Comparison to Guidance

| Feature | Outlines | Guidance |
|---------|----------|----------|
| Token healing | ❌ | ✅ |
| Multi-step workflows | ⚠️ limited | ✅ |
| Pydantic native | ✅ | ❌ |
| vLLM native | ✅ | ⚠️ |
| FSM fast-forward | ✅ | ❌ |
| Regex/grammar | ✅ | ✅ |

### References

- `references/json_generation.md` — JSON and Pydantic patterns
- `references/backends.md` — Backend configuration
- `references/examples.md` — Production examples

---

## Shared Best Practices

1. **Don't retry on constraint failure** — both frameworks guarantee valid output at generation time
2. **Use regex for format validation** — prefer `regex=` constraint over free generation
3. **Use enums/literals for fixed categories** — avoid string generation for known sets
4. **Add context in prompts** — helps the model generate correctly structured output
5. **Leverage backend strengths** — Outlines for Pydantic/vLLM, Guidance for token healing/multi-step
6. **Handle optional fields** — use `Optional[T] = None` for incomplete data
7. **Profile before optimizing** — both have minimal overhead, but Outlines' fast-forward can be 1.2-2x faster for deterministic paths