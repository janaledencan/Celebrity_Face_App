from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from faceapp.forms import UserForm
from faceapp.models import User

import tensorflow as tf
import numpy as np
from matplotlib import pyplot
from PIL import Image
from numpy import asarray
from mtcnn.mtcnn import MTCNN
from numpy import expand_dims

import urllib.request
import json
import os
import ssl


def extract_face(filename, required_size=(224, 224)):
	# load image from file
	pixels = pyplot.imread(filename)
	# create the detector, using default weights
	detector = MTCNN()
	# detect faces in the image
	results = detector.detect_faces(pixels)
	# extract the bounding box from the first face
	x1, y1, width, height = results[0]['box']
	x2, y2 = x1 + width, y1 + height
	# extract the face
	face = pixels[y1:y2, x1:x2]
	# resize pixels to the model size
	image = Image.fromarray(face)
	image = image.resize(required_size)

	face_array = asarray(image)
	return face_array


def allowSelfSignedHttps(allowed):
    # bypass the server certificate verification on client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context


def home(request):
    form = UserForm(initial={"sex": "M"})
    result_number=User.objects.count()
    context = {"form": form,
               "result_number": result_number
               }
    return render(request, "faceapp/home.html", context)


def post_user_data(request):
    form = UserForm(initial={"sex": "M"})
    class_names = ['Angelina Jolie', 'Brad Pitt', 'Denzel Washington', 'Hugh Jackman', 'Jennifer Lawrence', 'Johnny Depp', 'Kate Winslet', 'Leonardo DiCaprio', 'Megan Fox', 'Natalie Portman', 'Nicole Kidman', 'Robert Downey Jr', 'Sandra Bullock', 'Scarlett Johansson', 'Tom Cruise', 'Tom Hanks', 'Will Smith']


    if request.method == "POST":
        form = UserForm(request.POST, request.FILES)
        
                 
        image = request.FILES["uploaded_img"]

        # This is place where image or image location should go
        pixels = extract_face(image.name)

        # convert one face into samples
        pixels = pixels.astype('float32')
        samples = expand_dims(pixels, axis=0)

        allowSelfSignedHttps(True) # this line is needed if you use self-signed certificate in your scoring service.

        # Request data goes here
        # The example below assumes JSON formatting which may be updated
        # depending on the format your endpoint expects.
        # More information can be found here:
        # https://docs.microsoft.com/azure/machine-learning/how-to-deploy-advanced-entry-script
        data =  {
        "input_data": {'input_1':samples.tolist()},
        "params": {}
        }

        body = str.encode(json.dumps(data))

        url = 'https://ruap-actors-recognition-endpt.germanywestcentral.inference.ml.azure.com/score'
        # Replace this with the primary/secondary key or AMLToken for the endpoint
        api_key = 'p6oeUnLUs2Ib52gVvnnV0H5x9aovVfuV'
        if not api_key:
            raise Exception("A key should be provided to invoke the endpoint")

        # The azureml-model-deployment header will force the request to go to a specific deployment.
        # Remove this header to have the request observe the endpoint traffic rules
        headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key), 'azureml-model-deployment': 'celebrity-recognition-model-1' }

        req = urllib.request.Request(url, body, headers)

        try:
            response = urllib.request.urlopen(req)

            result = response.read() # % for all celebrities
            #print(result)
            predicted_labels = np.argmax(result, axis=-1) #most similar - index
            celebrity_name = ""

            for label in predicted_labels:
                celebrity_name = class_names[label]

            request.session['predictions'] = result

            if form.is_valid():
                user_post = User.objects.create(
                    age=form.cleaned_data.get("age"),
                    sex=form.cleaned_data.get("sex"),
                    predicted_face = celebrity_name,
                ).save()
                return HttpResponseRedirect(reverse("faceapp:post_user_data", args=[]))
            else:
                context = {"form": form, "image_form": image_form}
                return render(request, "faceapp/home.html", context)

        except urllib.error.HTTPError as error:
            print("The request failed with status code: " + str(error.code))

            # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
            print(error.info())
            print(error.read().decode("utf8", 'ignore'))
        
       

    else:
        form = UserForm()
        predictions = request.session.get('predictions')
        context = {"form": form, 
                   "predicted_values": predictions,
                   "names": class_names,
                   }
    return render(request, "faceapp/home.html", context)
