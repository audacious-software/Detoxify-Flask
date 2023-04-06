import json

from detoxify import Detoxify

from flask import Flask, current_app, request

app = Flask(__name__)

DETOXIFY_MODELS = (
    'original',
    'unbiased',
    'multilingual',
)

DETOXIFY_MODELS_ACTIVE = {}

@app.route('/', methods=['POST', 'GET'])
def score():
    to_score = request.form.get('s')
    
    if to_score is None:
        to_score = request.args.get('s')

    if to_score is None:
        to_score = 'Hello World!'

    scores = {
        'to_score': to_score
    }
    
    for model in DETOXIFY_MODELS:
        model_instance = DETOXIFY_MODELS_ACTIVE.get(model, None)
        
        if model_instance is None:
            model_instance = Detoxify(model)
            
            DETOXIFY_MODELS_ACTIVE[model] = model_instance

        model_scores = model_instance.predict(to_score)

        for key in model_scores:
            model_scores[key] = float(model_scores[key])

        scores[model] = model_scores
    
    return current_app.response_class(json.dumps(scores, indent=2), mimetype='application/json') # jsonify(scores)
