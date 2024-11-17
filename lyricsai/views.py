
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from lyricsai.models import Song, Artist
from lyricsai.forms import SongForm, LoginForm, SignupForm
from django.http import JsonResponse
from lyricsai.process_flow import process

def home(request):
    return render(request, 'home.html')

@login_required
def songs_view(request):
    """Display the list of songs and handle song addition.
    Only admin users can add or see songs.
    """
    # Check if the user is an admin
    if not request.user.is_staff:
        return render(request, 'admin_only.html')

    if request.method == 'POST':

        form = SongForm(request.POST)

        if form.is_valid():
            artist_name = form.cleaned_data['artist_name']
            print("artist_name", artist_name)
            artist, created = Artist.objects.get_or_create(name=artist_name)
            # Create the song instance with the new/existing artist
            song = Song(
                artist = artist,
                title = form.cleaned_data['title'])
            song.save()
            return redirect('songs')
    else:
        form = SongForm()

        # Fetch the list of songs to display
    songs = Song.objects.all()

    return render(request, 'songs.html', {'songs': songs, 'form': form})
def login_view(request):
    """Handle user login.
    The authenticated user is redirected to the songs page.
    If the user is not admin they will not have access the songs features.
    """
    if request.user.is_authenticated:
        return redirect('songs')  # Redirect authenticated users to a protected page

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('songs')  # Redirect to a protected page
            else:
                form.add_error(None, "Invalid username or password")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def signup_view(request):
    """Handle user signup.
    The registered user is automatically logged in.
    The user will not be admin automatically so they can't access the songs page.
    """
    if request.user.is_authenticated:
        return redirect('songs')  # Redirect authenticated users to a protected page

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('songs')  # Redirect to a protected page
    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})

def logout_view(request):
    """Logout the user and redirect to the login page."""

    logout(request)
    return redirect('login')


def artist_autocomplete(request):
    if 'term' in request.GET:
        qs = Artist.objects.filter(name__icontains=request.GET.get('term'))
        names = list(qs.values_list('name', flat=True))
        return JsonResponse(names, safe=False)
    return JsonResponse([], safe=False)


def analyze(request, song_id):
    """Analyze the song with the given id.

    This view is a placeholder for the song analysis logic.
    :param request: HTTP request
    :param song_id: song id
    """
    song = get_object_or_404(Song, id=song_id)
    if song:
        process(song)


    return JsonResponse({'OK': True})