'''
Sample handler for inference using Keras on AWS Lambda

@author: Sunil Mallya
'''
import json
import numpy as np
import tempfile
import time
import urllib2

from keras.models import Sequential
from keras.layers import Dense
from PIL import Image

# For ImageNet models 
from keras_squeezenet import SqueezeNet #using this lib to test SqueezeNet
from keras.applications.imagenet_utils import preprocess_input, decode_predictions
model = SqueezeNet()

def download_image(url):

    req = urllib2.urlopen(url)
    img_file = tempfile.NamedTemporaryFile(delete=True)
    img_file.write(req.read())
    img_file.flush()
    img = Image.open(img_file.name)
    img = img.resize((227, 227), Image.ANTIALIAS)
    x = np.asarray(img)
    x = np.expand_dims(x, axis=0)
    return x

def lambda_handler(event, context):
    
    url = ''
    try:
        # API Gateway GET method
        if event['httpMethod'] == 'GET':
            url = event['queryStringParameters']['url']
        # API Gateway POST method
        elif event['httpMethod'] == 'POST':
            data = json.loads(event['body'])
            url = data['url']
    except KeyError:
        # direct invocation
        url = event['url']
    
    handler_start_time = time.time()
    start_time = time.time()
    x = download_image(url)
    #requires scipy lib, can't use it since that puts us over 50MB zip limit for Lambda
    #x = preprocess_input(x) 
    preds = model.predict(x)
    end_time = time.time()
    print('Predicted:', decode_predictions(preds))
    h_time = end_time - handler_start_time
    p_time = end_time - start_time
    print("handler:", h_time ,"pred time:", p_time)
    return "%s,%s" % (h_time, p_time) 
