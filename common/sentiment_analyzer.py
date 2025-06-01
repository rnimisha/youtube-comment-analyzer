import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from transformers import XLMRobertaModel, XLMRobertaTokenizer

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = XLMRobertaTokenizer.from_pretrained("xlm-roberta-base")


class SentimentClassifier(nn.Module):
    def __init__(self, model):
        super(SentimentClassifier, self).__init__()
        self.model = model
        self.dropout = nn.Dropout(0.3)
        self.linear = nn.Linear(self.model.config.hidden_size, 2)

    def forward(self, input_ids, attention_mask):
        outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
        cls_output = outputs.last_hidden_state[:, 0, :]
        dropout_output = self.dropout(cls_output)
        return self.linear(dropout_output)


class InferenceDataset(Dataset):
    def __init__(self, texts, tokenizer, max_length):
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, index):
        encoding = self.tokenizer.encode_plus(
            str(self.texts[index]),
            add_special_tokens=True,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_attention_mask=True,
            return_tensors="pt",
        )
        return {
            "ids": encoding["input_ids"].flatten(),
            "attention_mask": encoding["attention_mask"].flatten(),
        }


def predict_sentiments(
    input_df,
    model_path,
    comment_name="comment",
    max_length=128,
    batch_size=16,
):
    # Load trained model
    base_model = XLMRobertaModel.from_pretrained("xlm-roberta-base")
    model = SentimentClassifier(base_model)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()

    dataset = InferenceDataset(input_df[comment_name].tolist(), tokenizer, max_length)
    loader = DataLoader(dataset, batch_size=batch_size)

    all_preds = []

    with torch.no_grad():
        for batch in loader:
            ids = batch["ids"].to(device)
            mask = batch["attention_mask"].to(device)
            outputs = model(ids, mask)
            preds = torch.argmax(outputs, dim=1)
            all_preds.extend(preds.cpu().numpy())

    input_df = input_df.copy()
    input_df["predicted_sentiment"] = all_preds
    input_df["sentiment_label"] = input_df["predicted_sentiment"].map(
        {0: "Negative", 1: "Positive"}
    )
    return input_df
