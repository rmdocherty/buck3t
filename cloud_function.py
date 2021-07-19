import base64
import numpy as np
import cv2
from PIL import Image, ImageOps
import io
from imageio import imread
from flask import jsonify
import traceback
import logging

def hello_world(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    try:
        headers = {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Origin, Content-Type, Accept',
                'Access-Control-Max-Age': '3600',
            }
        request_json = request.get_json()
            
        if request.method == 'OPTIONS':
            # Allows GET requests from any origin with the Content-Type
            # header and caches preflight response for an 3600s
            
            return ('', 204, headers)

        if request.args and 'message' in request.args:
            image = getImageFromB64(request.args.get('message'))
            jsoned = respond(image)
            return (jsoned, 200, headers)
            #return jsoned
        elif request_json and 'message' in request_json:
            image = getImageFromB64(request_json['message'])
            jsoned = respond(image)
            return (jsoned, 200, headers)
            #return jsoned
        else:

            return ("ugh", 200, headers)
            #return "shitshtishti"
    except Exception:
        test_header = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
        }

        data = traceback.format_stack()
        return (data, 200, test_header )

def blur(mat_size, image): #use 6
    kernel = np.ones((mat_size,mat_size),np.float32)/(mat_size**2)
    blur_img = cv2.filter2D(image,-1,kernel)
    return blur_img

def canny(K, thresh_min, thresh_max, image):#K = 4, min = 175, 180
    vectorized = image.reshape((-1,3))
    vectorized = np.float32(vectorized)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    attempts=10
    ret,label,center=cv2.kmeans(vectorized,K,None,criteria,attempts,cv2.KMEANS_PP_CENTERS)
    center = np.uint8(center)
    res = center[label.flatten()]
    res2 = res.reshape((image.shape))
    edges = cv2.Canny(res2,thresh_min,thresh_max)
    return edges

def joinGaps(gapiness, image): #gapiness = 2
    kernel = np.ones((gapiness,gapiness),np.uint8)
    closing = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    return closing

def dilate(size, image):
    kernel = np.ones((size,size),np.uint8)
    dilated = cv2.dilate(image, kernel)
    return dilated

def combineMethods(imageData):
    blurred = blur(6, imageData)
    cannied = canny(4, 175, 180, blurred)
    joined = joinGaps(2, cannied)
    dilated = dilate(3, joined)
    return dilated

def getImageFromB64(b64):
    imgdata = base64.standard_b64decode(b64)
    image = imread(io.BytesIO(imgdata))
    print(image, type(image))
    cv2_img = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    return cv2_img

def respond(image):
    stencil = combineMethods(image)
    imageFile = Image.fromarray(stencil)
    inverted = ImageOps.invert(imageFile)
    imgByteArr = io.BytesIO()
    inverted.save(imgByteArr, "bmp")
    imgByteData = imgByteArr.getvalue()
    #byteData = bytearray(imageFile)
    b64return = base64.b64encode(imgByteData)
    #json = jsonify(response=b64return)
    
    #r.headers.set('Access-Control-Allow-Origin', '*')
    #json.headers.set('Access-Control-Allow-Origin', '*')
    #json.headers.set('Access-Control-Allow-Methods', 'GET, POST')
    return b64return