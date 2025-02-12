from django.shortcuts import render
from .models import Tweet
from .forms import TweetForm, UserRegistrationForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import HttpResponseBadRequest


def tweet_list(request):
    tweets = Tweet.objects.all().order_by("-created_at")
    return render(request, "tweet_list.html", {"tweets": tweets})


@login_required
def tweet_create(request):
    if request.method == "POST":
        form = TweetForm(request.POST, request.FILES)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = request.user
            tweet.save()
            return redirect("tweet_list")

    else:
        form = TweetForm()
    return render(request, "tweet_form.html", {"form": form})


@login_required
def tweet_edit(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id, user=request.user)
    if request.method == "POST":
        form = TweetForm(request.POST, request.FILES, instance=tweet)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = request.user
            tweet.save()
            return redirect("tweet_list")
    else:
        form = TweetForm(instance=tweet)
    return render(request, "tweet_form.html", {"form": form})


@login_required
def tweet_delete(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id, user=request.user)
    if request.method == "POST":
        tweet.delete()
        return redirect("tweet_list")
    return render(request, "tweet_delete.html", {"tweet": tweet})


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password1"])
            user.save()
            login(request, user)
            return redirect("tweet_list")
    else:
        form = UserRegistrationForm()

    return render(request, "registration/register.html", {"form": form})


def tweet_search(request):
    if request.method == "POST":
        text_data = "Tweet with given text not found."
        text_search = request.POST.get(
            "search", ""
        ).strip()  # Get search input and strip any whitespace

        if not text_search:  # Check if search input is empty after stripping whitespace
            return render(request, "registration/index.html", {"text_data": text_data})

        queryset = Tweet.objects.filter(text__icontains=text_search).values(
            "user", "photo", "text", "id"
        )

        if not queryset.exists():
            return render(request, "registration/index.html", {"text_data": text_data})
        else:
            return render(request, "registration/index.html", {"queryset": queryset})
    else:
        # Handle GET request or initial load of the form
        return render(request, "registration/index.html")
