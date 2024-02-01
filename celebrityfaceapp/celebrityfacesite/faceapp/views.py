from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from faceapp.forms import UserForm
from faceapp.models import User


def home(request):
    form = UserForm(initial={"sex": "M"})
    context = {"form": form}
    return render(request, "faceapp/home.html", context)

def post_user_data(request):
    form = UserForm(initial={"sex": "M"})
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user_post = User.objects.create(
                age=form.cleaned_data.get("age"),
                sex=form.cleaned_data.get("sex"),
            ).save()
            return HttpResponseRedirect(reverse("faceapp:post_user_data", args=[]))
        else:
            context = {"form": form}
            return render(request, "faceapp/home.html", context)
    else:
        form = UserForm()
    return render(request, "faceapp/home.html", {"form": form})
