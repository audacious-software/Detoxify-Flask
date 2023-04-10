# pylint: disable=line-too-long

import json
import threading
import traceback

from flask import Flask, current_app, request, Response

from detoxify import Detoxify

app = Flask(__name__)

DETOXIFY_MODELS = (
    'original',
    'unbiased',
    'multilingual',
)

DETOXIFY_MODELS_ACTIVE = {}

LAST_TEXT = None
LAST_SCORES = None

WAIT_LOCK = threading.Semaphore()

@app.route('/', methods=['POST', 'GET'])
def score():
    global LAST_TEXT # pylint: disable=global-statement
    global LAST_SCORES # pylint: disable=global-statement

    to_score = request.form.get('s')

    if to_score is None:
        to_score = request.args.get('s')

    if to_score is None:
        to_score = 'Hello World!'

    scores = {
        'to_score': to_score
    }

    errored = False

    try:
        WAIT_LOCK.acquire() # pylint: disable=consider-using-with

        if to_score == LAST_TEXT:
            scores = LAST_SCORES
        else:
            for model in DETOXIFY_MODELS:
                model_instance = DETOXIFY_MODELS_ACTIVE.get(model, None)

                if model_instance is None:
                    print('[Detoxify] Creating model for "%s"...' % model)
                    model_instance = Detoxify(model)

                    DETOXIFY_MODELS_ACTIVE[model] = model_instance

                    print('[Detoxify] Model "%s" created and persisted to memory.' % model)

                model_scores = model_instance.predict(to_score)

                for key in model_scores:
                    model_scores[key] = float(model_scores[key])

                scores[model] = model_scores

            LAST_TEXT = to_score
            LAST_SCORES = scores
    except: # pylint: disable=bare-except
        traceback.print_exc()

        errored = True
    finally:
        WAIT_LOCK.release()

    if errored:
        return Response('Error encountered scoring "%s". Check logs for full details.' % to_score, status=500)

    return current_app.response_class(json.dumps(scores, indent=2), mimetype='application/json') # jsonify(scores)
