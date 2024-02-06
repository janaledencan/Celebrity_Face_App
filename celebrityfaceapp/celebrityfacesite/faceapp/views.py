from heapq import nlargest
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from faceapp.forms import UserForm, ImageForm
from faceapp.models import User

import tensorflow as tf
import numpy as np
from matplotlib import pyplot
from PIL import Image
from numpy import asarray
from mtcnn.mtcnn import MTCNN
from numpy import expand_dims

import plotly as pl

import urllib.request
import json
import os
import ssl

from django.core.files.uploadedfile import SimpleUploadedFile
from plotly.offline import plot
import plotly.graph_objects as go


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

    #-------------------------------------------------------Added by Nikola-----------------------------------------------------------#
    fig = pl.graph_objs.Figure(data=[pl.graph_objs.Bar(x=['Male','Female'],y=[135,111])])
    graph_div = pl.offline.plot(fig, auto_open = False, output_type="div")
    #---------------------------------------------------------------------------------------------------------------------------------#

    result_number=User.objects.count()
    context = {"form": form,
               "result_number": result_number,
               "graph_div":graph_div
               }
    return render(request, "faceapp/home.html", context)


def post_user_data(request):
  
    class_names = ['Angelina Jolie', 'Brad Pitt', 'Denzel Washington', 'Hugh Jackman', 'Jennifer Lawrence', 'Johnny Depp', 'Kate Winslet', 'Leonardo DiCaprio', 'Megan Fox', 'Natalie Portman', 'Nicole Kidman', 'Robert Downey Jr', 'Sandra Bullock', 'Scarlett Johansson', 'Tom Cruise', 'Tom Hanks', 'Will Smith']

    if request.method == "POST":
        form = UserForm(request.POST, request.FILES)

        #graph_div = pl.offline.plot(fig, auto_open = False, output_type="div")

        if form.is_valid():
            user=form.save(commit=False)
            user.predicted_face="BP"
            user.save()
            
            return HttpResponseRedirect(reverse("faceapp:post_user_data", args=[]))
        else:
             form = UserForm()
             return render(request, "faceapp/home.html", {'form': form})
        
    req=User.objects.latest('id')
   
    context = {
        'celebrities':class_names, 
        "req": req
        }
    return render(request, "faceapp/result.html", context)




def get_prediction(request, req_id):
     
    user_input = User.objects.get(pk=req_id)
    class_names = ['Angelina Jolie', 'Brad Pitt', 'Denzel Washington', 'Hugh Jackman', 'Jennifer Lawrence', 'Johnny Depp', 'Kate Winslet', 'Leonardo DiCaprio', 'Megan Fox', 'Natalie Portman', 'Nicole Kidman', 'Robert Downey Jr', 'Sandra Bullock', 'Scarlett Johansson', 'Tom Cruise', 'Tom Hanks', 'Will Smith']

    if user_input is not None:

        image_path = user_input.image
        pixels = extract_face(image_path)

        # convert one face into samples
        pixels = pixels.astype('float32')
        samples = expand_dims(pixels, axis=0)

        allowSelfSignedHttps(True) # this line is needed if you use self-signed certificate in your scoring service.

  
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

            result = response.read() #bytestring

            # Remove the outer brackets and split by commas to get a list of strings
            list_of_strings = result.decode().strip('[]').split(', ')

            # Convert the list of strings to a list of floats
            list_of_floats = [float(s) for s in list_of_strings]

            # Create a NumPy array from the list of floats
            numpy_array = np.array(list_of_floats, dtype=np.float64)

           
            percent_array = numpy_array *  100
            # Round each element to  12 decimal places
            rounded_array = np.around(percent_array, decimals=12)


            results_dict = dict(zip(class_names, rounded_array))

            # Extract the top  5 items using nlargest()
            top_five_items = nlargest(5, results_dict.items(), key=lambda x: x[1])

            # Convert the list of tuples back into a dictionary
            top_five_dict = dict(top_five_items)

            #change predicted_face value of object with the name of the class with the highest score
            predicted_label = np.argmax(numpy_array, axis=-1) #most similar - index
        
            celebrity_name = class_names[predicted_label]

            user_input.predicted_face = celebrity_name
            user_input.save()
            
            print(result)
        except urllib.error.HTTPError as error:
            print("The request failed with status code: " + str(error.code))

            # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
            print(error.info())
            print(error.read().decode("utf8", 'ignore'))

        celebrity_image_path = PickLookalikeImage(celebrity_name)

        ### Pie chart
        labels = list(top_five_dict.keys())
        data = list(top_five_dict.values())

        fig = go.Figure(data=[go.Pie(labels=labels, values=data, hole=0.5)])
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',  # set background color to transparent
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=0, b=0, l=0, r=0),
            autosize=False,
            width=600,
            height=300 
        )
        graph_div = plot(fig, auto_open=False, output_type="div")
        ### end Pie chart

        context = {
            "results": top_five_dict, 
            "req": user_input, 
            "celebrity_name": celebrity_name,
            "celebrity_image_path" : celebrity_image_path,
            "graph_div" : graph_div,
        }
        return render(request, 'faceapp/result.html', context)

    
def PickLookalikeImage(celebrity_name):
    image_path = ""
    name = celebrity_name.split()
    image_path += name[0] + "" + name[1][0] + ".jpg"
    return image_path

