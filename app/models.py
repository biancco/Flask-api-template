from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch

class MyModel:
    def __init__(self, device="cpu"):
        self.device = torch.device(device)
        self.model_name='t5-small'
        self.tokenizer = T5Tokenizer.from_pretrained(self.model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(self.model_name).to(self.device)

    def predict(self, text):
        prefix = "summarize: "
        input_text = prefix+text

        inputs = self.tokenizer.encode_plus(
            input_text,
            max_length=512,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        input_ids = inputs["input_ids"].to(self.device)
        attention_mask = inputs["attention_mask"].to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                max_length=150,
                early_stopping=True
            )
            
        decoded_outputs = [self.tokenizer.decode(output, skip_special_tokens=True) for output in outputs]
        return decoded_outputs[0]