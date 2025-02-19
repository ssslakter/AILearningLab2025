import sys
sys.path.append("..")
import onnxruntime as ort
import numpy as np
from transformers import AutoTokenizer, AutoConfig
from src.preprocess import preprocess_data, postprocess_labels
import logging as l
import pandas as pd

l.basicConfig(level=l.INFO)

def pipe(texts, bs=1):
    l.info('tokenized')
    predictions = []
    for i in range(0, len(texts), bs):
        batch = texts[i:i + bs]
        inputs = tokenizer(batch, padding=True, truncation=True, return_tensors="np")
        onnx_inputs = {k: v for k, v in inputs.items()}
        onnx_outputs = ort_session.run(None, onnx_inputs)
        batch_predictions = np.argmax(onnx_outputs[0], axis=1)
        predictions.extend([model_config.id2label[p] for p in batch_predictions])
    l.info('predictions made')
    return predictions

def main():
    input_path = "/contest/data.csv"
    output_path = "/contest/submission.csv"
    l.info(f"Reading data from {input_path}")
    data = pd.read_csv(input_path, encoding='utf-8', delimiter=',', quotechar='"')
    if "MessageText" not in data.columns: raise ValueError("Invalid input file structure, missing 'MessageText' column.")
    data = preprocess_data(data)
    texts = data['Text']
    l.info(f"Starting classification, size: {len(texts)}")
    res = pipe(texts.tolist())
    data["Class"] = postprocess_labels(res)
    data[["UserSenderId", "Class"]].to_csv(output_path, index=False)
    l.info(f"Processing complete. Output written to {output_path}")


if __name__ == "__main__":
    l.info("Loading model...")
    model_folder = 'onnx'
    tokenizer = AutoTokenizer.from_pretrained(model_folder)
    model_config = AutoConfig.from_pretrained(model_folder)
    ort_session = ort.InferenceSession(f"{model_folder}/model.onnx")
    l.info("Model loaded. Device: cpu")
    main()