from flask import current_app

from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch

class SumModel:
    def __init__(self, device="cpu"):
        self.device = torch.device(device)
        self.model_name='t5-small'
        self.tokenizer = T5Tokenizer.from_pretrained(self.model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(self.model_name).to(self.device)
        self.model.eval()

    @ torch.no_grad()
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

        outputs = self.model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_length=150,
            early_stopping=True
        )
            
        decoded_outputs = [self.tokenizer.decode(output, skip_special_tokens=True) for output in outputs]
        return decoded_outputs[0]


from transformers import DetrImageProcessor, DetrForObjectDetection
from PIL import Image

class ObjectDetector:
    def __init__(self, model_name="facebook/detr-resnet-50", device="cpu") -> None:
        self.device = torch.device(device)
        self.model_name = model_name
        self.processor = DetrImageProcessor.from_pretrained(self.model_name)
        self.model = DetrForObjectDetection.from_pretrained(self.model_name).to(self.device)
        self.model.eval()

    @ torch.no_grad()
    def predict(self, image:Image):
        inputs = self.processor(images=image, return_tensors="pt")
        outputs = self.model(
            pixel_values=inputs["pixel_values"].to(self.device),
            pixel_mask=inputs["pixel_mask"].to(self.device),
        )
        target_sizes = torch.tensor([image.size[::-1]])
        results = self.processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.9)[0]
        
        res_tuple = []
        for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
            box = [round(i, 2) for i in box.tolist()]
            res_tuple.append((self.model.config.id2label[label.item()],box,round(score.item(), 3)))
        return res_tuple
        

from transformers import GLPNFeatureExtractor, GLPNForDepthEstimation
import numpy as np

class DepthEstimation:
    def __init__(self, model_name="vinvino02/glpn-nyu", device="cpu") -> None:
        self.device = torch.device(device)
        self.model_name = model_name
        self.feature_extractor = GLPNFeatureExtractor.from_pretrained(self.model_name)
        self.model = GLPNForDepthEstimation.from_pretrained(self.model_name).to(self.device)
        self.model.eval()

    @ torch.no_grad()
    def predict(self, image:Image): 
        inputs = self.feature_extractor(images=image, return_tensors="pt")
        outputs = self.model(
            pixel_values=inputs["pixel_values"].to(self.device),
        )
        predicted_depth = outputs.predicted_depth
        prediction = torch.nn.functional.interpolate(
            predicted_depth.unsqueeze(1),
            size=image.size[::-1],
            mode="bicubic",
            align_corners=False,
        )
        output = prediction.squeeze().cpu().numpy()
        formatted = (output * 255 / np.max(output)).astype("uint8")
        depth = Image.fromarray(formatted)
        return depth
        

from transformers import VitsModel, AutoTokenizer
import io
import scipy

class TTSModel:
    def __init__(self, model_name="facebook/mms-tts-eng", device="cpu") -> None:
        self.device = torch.device(device)
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = VitsModel.from_pretrained(self.model_name).to(self.device)
        self.model.eval()

    @ torch.no_grad()
    def predict(self, text:str): 
        inputs = self.tokenizer(text=text, return_tensors="pt")
        output = self.model(
            input_ids=inputs["input_ids"].to(self.device),
            attention_mask=inputs["attention_mask"].to(self.device),
        ).waveform.cpu().float().numpy()
        
        output = np.transpose(output)
        
        audio_bytes_io = io.BytesIO()
        audio_bytes_io.name = 'result.wav'
        
        scipy.io.wavfile.write(audio_bytes_io, rate=self.model.config.sampling_rate, data=output)
        return audio_bytes_io.getvalue()


from transformers import WhisperProcessor, WhisperForConditionalGeneration

class STTModel:
    def __init__(self, model_name="openai/whisper-small", device="cpu") -> None:
        self.device = torch.device(device)
        self.model_name = model_name
        self.processor = WhisperProcessor.from_pretrained(self.model_name)
        self.model = WhisperForConditionalGeneration.from_pretrained(self.model_name).to(self.device)
        self.model.config.forced_decoder_ids = None
        self.model.eval()

    @ torch.no_grad()
    def predict(self, audio_bytes:bytes): 
        samplerate, data = scipy.io.wavfile.read(io.BytesIO(audio_bytes))
        input_features = self.processor(data, sampling_rate=samplerate, return_tensors="pt").input_features
        
        predicted_ids = self.model.generate(input_features.to(self.device))
        transcription = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)
        return transcription

        
        
        