from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
import re
from . import util
import random as rand
import markdown2

class Search(forms.Form):
    query = forms.CharField(label="Search Encyclopedia")

class NewPage(forms.Form):
    title = forms.CharField()
    markdown = forms.CharField(widget=forms.Textarea)

def index(request):
    if "saved_entries" not in request.session:
        request.session["saved_entries"] = []
    #search form
    if request.method == "POST":
        form = Search(request.POST)
        if form.is_valid():
            new_entry = form.cleaned_data["query"]
            if util.get_entry(title=new_entry):
                return HttpResponseRedirect(f"{new_entry}")
            request.session["saved_entries"] = [i for i in util.list_entries() if re.search(new_entry,i, re.IGNORECASE)]
            return render(request, "encyclopedia/results.html", {
                "results": request.session["saved_entries"]
            })
        else:
            return render(request, "encyclopedia/index.html", {
                "entries": util.list_entries(),
                "form": Search
            })
    else:
        request.session["saved_entries"] = util.list_entries()
        return render(request, "encyclopedia/index.html", {
            "entries": request.session["saved_entries"],
            "form": Search
    })

def entry(request,title):
    if title in request.session["saved_entries"]:
        request.session["latest"] = title
    return render(request,"encyclopedia/entry.html", {
        "entry": util.get_entry(title=title),
    })

def new_page(request):
    if request.method == "POST":
        data = NewPage(request.POST)
        if data.is_valid():
            title = data.cleaned_data["title"]
            if util.get_entry(title=title) == None: #there are no other titles with the same name
                util.save_entry(title, markdown2.markdown(data.cleaned_data["markdown"])) #save the entry
                request.session["saved_entries"] += util.get_entry(title=title)
                request.session["latest"] = title
                return HttpResponseRedirect(f"{title}")
            else:
                return render(request, "encyclopedia/new_page.html", {
                    "message": "Please try another title"
                })
    else:
        return render(request, "encyclopedia/new_page.html", {
            "message": NewPage
        })

def edits(request):
    if request.method == "POST":
        data = request.POST['data']
        util.save_entry(title=request.session["latest"],content=data)
        return HttpResponseRedirect(f"{request.session['latest']}")
    return render(request, "encyclopedia/edits.html", {
        "content": util.get_entry(request.session["latest"])
    })

def random(request):
    rando = rand.choice(request.session["saved_entries"])
    return HttpResponseRedirect(f"{rando}")

