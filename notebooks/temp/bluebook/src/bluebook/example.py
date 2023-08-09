import torch
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained("facebook/opt-350m", load_in_4bit=True, device_map="auto")

def list_gpus():
    num_gpus = torch.cuda.device_count()
    return [torch.cuda.get_device_name(i) for i in range(num_gpus)]

def list_models():
    return model    