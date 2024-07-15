
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS  
app = Flask(__name__)
CORS(app)  

import numpy as np
import pandas as pd
import nltk
from transformers import BertTokenizer, BertModel
import torch
from scipy.spatial.distance import cosine
import speech_recognition as sr
import pickle
import pyttsx3
import requests
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt

nltk.download('punkt')

huggingface_model = 'bert-base-uncased'
model = BertModel.from_pretrained(huggingface_model)
tokenizer = BertTokenizer.from_pretrained(huggingface_model)

with open('product_embeddings.pkl', 'rb') as f:
    data = pickle.load(f)
    product_embeddings = data['product_embeddings']
    product_ids = data['product_ids']
    product_names = data['product_names']
    product_descriptions = data['product_descriptions']

engine = pyttsx3.init()

# Function to calculate BERT embedding for an input sentence
def calculate_input_embedding(input_sentence):
    input_sentence_encoded = tokenizer.encode_plus(input_sentence, add_special_tokens=True, return_tensors='pt', truncation=True)
    input_ids = input_sentence_encoded['input_ids']
    attention_mask = input_sentence_encoded['attention_mask']

    with torch.no_grad():
        output = model(input_ids, attention_mask=attention_mask)

    input_embedding = output.last_hidden_state[:, 0, :].numpy()[0] 
    input_embedding = input_embedding.astype(np.float32)  
    return input_embedding

def find_most_similar_products(input_sentence):
    input_embedding = calculate_input_embedding(input_sentence)

    # Calculate cosine similarity between input sentence embedding and each product embedding
    similarities = []
    for prod_emb in product_embeddings:
        sim_score = 1 - cosine(input_embedding, prod_emb)
        similarities.append(sim_score)

    most_similar_indices = np.argsort(similarities)[-6:][::-1] 
    most_similar_products = [{
        'id': int(product_ids[idx]),  
        'name': product_names[idx],
        'description': product_descriptions[idx]
    } for idx in most_similar_indices]

    output_text = f"Input Sentence: {input_sentence}\n"
    for i, product in enumerate(most_similar_products):
        output_text += f"Rank {i+1}: Product ID: {product['id']}, Product Name: {product['name']}\n"

    print(output_text)
    engine.say("Here are suggestions for you")
    for product in most_similar_products:
        display_image_from_url(product['description'])  
    engine.runAndWait()

# Function to capture speech input and convert to text
def get_speech_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Please say something...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
    return None

# Function to display image from URL using Matplotlib
def display_image_from_url(image_url):
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    plt.imshow(img)
    plt.axis('off')  
    plt.show()

# Endpoint to get the most similar product
@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    input_sentence = data.get('input_sentence')
    input_embedding = calculate_input_embedding(input_sentence)

    # Calculate cosine similarity between input sentence embedding and each product embedding
    similarities = []
    for prod_emb in product_embeddings:
        sim_score = 1 - cosine(input_embedding, prod_emb)
        similarities.append(sim_score)

    most_similar_indices = np.argsort(similarities)[-6:][::-1]  
    most_similar_products = [{
        'product_id': int(product_ids[idx]), 
        'product_name': product_names[idx],
        'product_description': product_descriptions[idx]  
    } for idx in most_similar_indices]

    response = {
        'products': most_similar_products  
    }

    return make_response(jsonify(response), 200)

if __name__ == '__main__':
    app.run(debug=True)



