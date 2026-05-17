from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

MODEL_NAME = "google/flan-t5-base"

# Load once at startup
print("🔄 Loading local LLM model... (first time may take 10-20 seconds)")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

# Force CPU (safe for deployment)
device = torch.device("cpu")
model.to(device)
model.eval()


def generate_text(prompt: str, max_tokens: int = 200, temperature: float = 0.5):

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=1024
    )

    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            do_sample=False
        )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return response.strip()