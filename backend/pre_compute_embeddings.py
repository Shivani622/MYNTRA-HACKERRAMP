import numpy as np
import pandas as pd
import nltk
from transformers import BertTokenizer, BertModel
import torch
import pickle

# Download NLTK punkt tokenizer if not already downloaded
nltk.download('punkt')

# Initialize BERT tokenizer and model
huggingface_model = 'bert-base-uncased'
model = BertModel.from_pretrained(huggingface_model)
tokenizer = BertTokenizer.from_pretrained(huggingface_model)

# Specify path to your CSV file
csv_file_path = 'backend/fashion.csv'

# Batch processing parameters
batch_size = 16  # Adjust batch size as per your hardware capabilities and dataset size

# Function to calculate BERT embeddings for a batch of descriptions
def calculate_embeddings(descriptions):
    embeddings = []
    for description in descriptions:
        product_name = description['ProductTitle']
        product_description = f"{description['Colour']}{product_name}"
        encoded_dict = tokenizer.encode_plus(product_description, add_special_tokens=True, return_tensors='pt', truncation=True)
        product_input_ids = encoded_dict['input_ids']
        product_attention_mask = encoded_dict['attention_mask']

        with torch.no_grad():
            output = model(product_input_ids, attention_mask=product_attention_mask)

        product_embedding = output.last_hidden_state[:, 0, :].numpy()[0]  # CLS token embedding, selecting the first sentence
        product_embedding = product_embedding.astype(np.float32)  # Ensure float32 type
        embeddings.append(product_embedding)

    return embeddings

# Load dataset from CSV file in chunks/batches
product_embeddings = []
product_ids = []
product_names = []
product_descriptions = []

for chunk in pd.read_csv(csv_file_path, chunksize=batch_size):
    chunk_embeddings = calculate_embeddings(chunk.to_dict('records'))
    product_embeddings.extend(chunk_embeddings)
    product_ids.extend(chunk['ProductId'].values)
    product_names.extend(chunk['ProductType'].values)
    product_descriptions.extend(chunk['ImageURL'].values)

# Save embeddings and metadata to a file
with open('product_embeddings.pkl', 'wb') as f:
    data = {
        'product_embeddings': product_embeddings,
        'product_ids': product_ids,
        'product_names': product_names,
        'product_descriptions': product_descriptions
    }
    pickle.dump(data, f)