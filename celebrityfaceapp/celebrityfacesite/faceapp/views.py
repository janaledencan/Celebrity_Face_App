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

import urllib.request
import json
import os
import ssl

from django.core.files.uploadedfile import SimpleUploadedFile



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
    #form = UserForm(initial={"sex": "M"})
    #form =ImageForm(initial={"sex": "M"})
    class_names = ['Angelina Jolie', 'Brad Pitt', 'Denzel Washington', 'Hugh Jackman', 'Jennifer Lawrence', 'Johnny Depp', 'Kate Winslet', 'Leonardo DiCaprio', 'Megan Fox', 'Natalie Portman', 'Nicole Kidman', 'Robert Downey Jr', 'Sandra Bullock', 'Scarlett Johansson', 'Tom Cruise', 'Tom Hanks', 'Will Smith']


    if request.method == "POST":
        form = UserForm(request.POST, request.FILES)

        if form.is_valid():
            user=form.save(commit=False)
            user.predicted_face="BP"
            user.save()

            return HttpResponseRedirect(reverse("faceapp:post_user_data", args=[]))
        else:
             form = UserForm()
             return render(request, "faceapp/home.html", {'form': form})
        
        

        #form = ImageForm(request.POST, request.FILES)
        #image = request.FILES["uploaded_img"]

        #context = {"image": image}
        #return render(request, "faceapp/result.html", context)
        
    return render(request, "faceapp/result.html", {'celebrities':class_names,})


def get_prediction(request):
     