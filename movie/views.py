from django.shortcuts import render,redirect
from requests.adapters import HTTPAdapter
from django.contrib.auth.models import User,auth
from urllib3.util.retry import Retry

import requests
import pandas as pd
import numpy as np



movies = pd.read_pickle("C:\\Users\\Barath Raj\\Downloads\\movie_list.pkl")
similarity = pd.read_pickle("C:\\Users\\Barath Raj\\OneDrive\\similarity (1).pkl")
filtermovie = pd.read_pickle("C:\\Users\\Barath Raj\\Downloads\\filtermovie.pkl")
filtersimilarity = pd.read_pickle("C:\\Users\\Barath Raj\\OneDrive\\filtersimilarity.pkl")

def login(request):
    if request.method=='POST':
        username=request.POST['email']
        password=request.POST['password']
        user=auth.authenticate(request,username=username,password=password)
        if user is not None:
            auth.login(request,user)
            return redirect('home')
        else:
            return redirect('signup')
    return render(request,'login.html')

def signup(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        email=request.POST['email']
        phoneno=request.POST['phoneno']
        confirm_pass=request.POST['confirmpass']
        if password==confirm_pass:
            user=User.objects.create_user(username=username,email=email,password=password)
            user.save()
            return redirect('login')
    return render(request,'signup.html')

def home(request):
    recommended_movie_posters = []
    recommended_movie_names = []
    movie_list = movies['title'].values
    recommended_movie_names, recommended_movie_posters = recommend('Avatar')
    title,poster=recommend_movies('Horror',filtermovie,filtersimilarity)

    if request.method=='GET':
        selected_movie = request.GET.get('movie_select')
        genre=request.GET.get('genre')
        if genre:
            title,poster=recommend_movies(genre,filtermovie,filtersimilarity)
        if selected_movie:   
            recommended_movie_names, recommended_movie_posters = recommend(selected_movie)

        movies_data = list(zip(title, poster))
            

    return render(request, 'home.html', {
        'recommended_movie_posters': recommended_movie_posters,
        'movie_list': movie_list,
        'name': recommended_movie_names,
        'movies_data':movies_data
    })

def recommend_movies(genre, new, cosine_sim):
    indices = new[new['tags'].str.contains(genre)].index
    similar_movies = []

    for idx in indices:
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:6]
        movie_indices = [i[0] for i in sim_scores]
        similar_movies.extend([(new['title'].iloc[i], new['movie_id'].iloc[i]) for i in movie_indices])
    poster=[]
    title=[]
    for i in similar_movies[:12]:
        poster.append(fetch_poster(i[1]))
        title.append(i[0])


    return title,poster




    
def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    retries = Retry(total=5, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retries))
    data = session.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:16]:
        
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names,recommended_movie_posters


