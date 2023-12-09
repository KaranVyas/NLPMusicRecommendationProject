from transformers import BertTokenizer, BertForSequenceClassification
import torch

def get_emotion_from_text(text):
    # Load the tokenizer and model
    model_path = './saved_model'
    tokenizer = BertTokenizer.from_pretrained(model_path)
    model = BertForSequenceClassification.from_pretrained(model_path)

    # If using GPU, move the model to GPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # Function to preprocess the text
    def preprocess_text(text, tokenizer, max_length=512):
        inputs = tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=max_length,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        return inputs['input_ids'], inputs['attention_mask']

    # Preprocess the text
    input_ids, attention_mask = preprocess_text(text, tokenizer)

    # Move inputs to the appropriate device
    input_ids = input_ids.to(device)
    attention_mask = attention_mask.to(device)

    # Make prediction
    model.eval()  # Set the model to evaluation mode
    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_mask)

    # Process the output
    logits = outputs.logits
    predictions = torch.sigmoid(logits).cpu().numpy()  # Use sigmoid for multi-label classification

    # Assuming a threshold of 0.5 for determining the label presence
    threshold = 0.5
    predicted_labels = (predictions > threshold).astype(int)

    # Mapping the predictions to the emotion labels
    emotions = [
        "Happiness", "Contentment", "Confidence", "Neutral", "Sadness",
        "Anger", "Fear", "Surprise", "Disgust", "Love",
        "Excitement", "Anticipation", "Nostalgia", "Confusion",
        "Frustration", "Longing", "Optimism"
    ]

    predicted_emotions = [emotion for emotion, label in zip(emotions, predicted_labels[0]) if label == 1]
    return predicted_emotions

# Example usage
predicted_emotions = get_emotion_from_text("hey i love you")
print("Predicted Emotions:", predicted_emotions)
