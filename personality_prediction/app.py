from flask import Flask, request, jsonify, render_template
import torch
from transformers import BertTokenizer, BertModel
from MLPClassifier import MLPClassifier

# # set up logging 
# import logging
# logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s')
# logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load the tokenizer and model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

# load classifier
classifier = MLPClassifier(input_dim=768, hidden_dim=512, output_dim=5)

# state dicts path
classifier_save_path = '/Users/yor/goorm_python/hw5/classifier_model.pth'
bert_model_save_path = '/Users/yor/goorm_python/hw5/bert_model.pth'

# Load state dicts
model.load_state_dict(torch.load(bert_model_save_path, map_location=torch.device('cpu')))
classifier.load_state_dict(torch.load(classifier_save_path, map_location=torch.device('cpu')))

# Set model and classifier to evaluation mode
model.eval()
classifier.eval()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'text' in request.form:
        text = request.form['text']
    else:
        # If not, try to get it from JSON body
        data = request.get_json(force=True)
        if 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        text = data['text']
    
    
    # Tokenize and prepare input
    inputs = tokenizer(text, padding=True, truncation=True, max_length=512, return_tensors="pt")
    input_ids = inputs['input_ids']
    attention_mask = inputs['attention_mask']
    
    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_mask)
        pooled_output = outputs.pooler_output
        logits = classifier(pooled_output)
        predictions = torch.sigmoid(logits)
        
        # Debug: Print or log the shape and content of predictions
        print(f"Predictions shape: {predictions.shape}")
        print(f"Predictions: {predictions}")
        predicted_classes = (predictions > 0.5).int().tolist()  # Binary classification threshold

    if 'text' in request.form:
        predicted_traits = ['High' if trait >= 0.5 else 'Low' for trait in predictions[0]]
        return render_template('results.html', predicted_traits=predicted_traits) #,debug_info=f"Predictions shape: {predictions.shape}, Predictions: {predictions.tolist()}"

    else:
        return jsonify(predicted_classes)
    
if __name__ == '__main__':
    app.run(debug=True)

"""
About the issues that I've gone through:
This adjustment is specifically suitable for single-item predictions where your batch size is 1. 
If you were to scale this application to handle multiple inputs simultaneously, 
you would need to adjust your approach to process each input's predictions accordingly, 
likely involving an additional loop over the batch dimension.

The resolution of the initial issue underscores the importance of carefully managing tensor dimensions, 
especially in tasks involving multiple outputs or classes. 
It's a common source of bugs in machine learning and deep learning applications, 
where the distinction between batch size and number of features/classes must be clearly maintained throughout 
preprocessing, model prediction, and postprocessing stages.
"""