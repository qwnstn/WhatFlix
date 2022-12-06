from django.http import HttpResponse, JsonResponse
import json
import random
import requests
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.shortcuts import get_object_or_404, get_list_or_404
from .serializers import MovieListSerializer, MovieSerializer, CastSerializer, PosterSerializer ,GenreListSerializer, ProviderSerializer, CinemaSerializer
from .models import Movie, Genre, Cast, Poster, History, Provider, Cinema
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from django.utils import timezone
import pandas


# def csv_to_DB(request):
#     data = pandas.read_csv("./movies/example.csv")
#     filter_data = data.filter(items=['POI_NM', 'CTPRVN_NM','SIGNGU_NM', 'LEGALDONG_NM', 'LC_LO', 'LC_LA'])
#     total_cnt = len(filter_data)
#     for i in range(total_cnt):
#         Cinema.objects.create(
#             name = filter_data.loc[i][0],
#             metropolitan_city = filter_data.loc[i][1],
#             district = filter_data.loc[i][2],
#             region = filter_data.loc[i][3],
#             latitude = filter_data.loc[i][4],
#             altitude = filter_data.loc[i][5]
#             )
    
@api_view(['GET'])
def cinema_list(request):
    '''
    주어진 3가지의 주소 데이터를 통해 해당 영화관 찾아서 반환하는 함수
    '''
    metropolitan_city = request.GET.get('metropolitan_city')
    district = request.GET.get('district')
    region = request.GET.get('region')
    cinema = Cinema.objects.filter(metropolitan_city=metropolitan_city).filter(district=district).filter(region=region)
    if len(cinema) == 1:
        serializer = CinemaSerializer(cinema[0])
        return Response(serializer.data)
    elif len(cinema) >= 2:
        serializer = CinemaSerializer(cinema, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def district_list(request, city):
    '''
    city를 선택하고 나서 데이터를 받은 후에 district의 옵션을 결정해주기 위한 함수
    예를 들어, 강원도가 선택되어지면 그에 따른 구들이 옵션에 나타나도록 할 예정
    '''
    cinemas = Cinema.objects.filter(metropolitan_city=city)
    selectcity = cinemas.order_by('district')
    results = selectcity.values_list('district', flat=True).distinct()
    return Response(results)


@api_view(['GET'])
def region_list(request, city, district):
    cinemas = Cinema.objects.filter(metropolitan_city=city).filter(district=district)
    selectcity = cinemas.order_by('region')
    results = selectcity.values_list('region', flat=True).distinct()
    return Response(results)


@api_view(['GET'])
def movie_provieder(request, movie_id):
    providers = get_list_or_404(Provider, movie_id = movie_id)
    serializer = ProviderSerializer(providers, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def movie_upcoming(request):
    movies = Movie.objects.all().filter(release_date__range=[date.today() - timedelta(days=30), date.today()])
    if len(movies) >= 10:
        movies = random.sample(list(movies), 10)
    serializer = MovieListSerializer(movies, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def movie_history(request, movie_pk):
    movie = get_object_or_404(Movie, movie_id=movie_pk)
    serializer = MovieListSerializer(movie)
    genres = serializer.data['genres']
    if request.method == 'POST':
        user = request.user
        for genre in genres:
            History.objects.create(
                user_id = user.id,
                movie_id = movie_pk,
                genres = genre,
                score = 1
            )
        return Response(status=status.HTTP_201_CREATED)


@api_view(['GET'])
def movie_list(request):
    movies = get_list_or_404(Movie)
    serializer = MovieListSerializer(movies, many=True)
    # print(serializer.data)
    return Response(serializer.data)


@api_view(['GET'])
def movie_detail(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    serializer = MovieSerializer(movie)
    # print(serializer.data)
    return Response(serializer.data)

@api_view(['GET', 'POST'])
def movie_like(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    user = request.user
    if request.method == 'GET':
        liked = True
        if user in movie.like_users.all():
            liked = True
        else:
            liked = False
        return Response({'liked': liked})
    elif request.method == 'POST':
        if user in movie.like_users.all():
            movie.like_users.remove(user)
            data = {'liked': False}
            return Response(data, status=status.HTTP_204_NO_CONTENT)
        else:
            movie.like_users.add(user)
            data = {'liked': True}
            return Response(data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def movie_trend(request):
    movie_dict = {}
    trends = History.objects.filter(updated_at__gte = timezone.now() - timedelta(days=7))
    for trend in trends:
        movie = trend.movie_id
        if movie in movie_dict:
            movie_dict[movie] += 1
        else:
            movie_dict[movie] = 1

    li = []
    for j in movie_dict.items():
        li.append(j)
    li.sort(key=lambda x: x[1], reverse=True)
    total_li = []
    cnt = 0
    for k in li:
        trend_movie = Movie.objects.get(movie_id=k[0])
        total_li.append(trend_movie)
        cnt += 1
        if cnt == 10:
            break
    serializer = MovieListSerializer(total_li, many=True)
    return Response(serializer.data)



@api_view(['GET'])
def movie_recommend(request):
    user = request.user
    actions = History.objects.all().filter(user_id=user.id)
    length = actions.count()
    if length == 0:
        return Response(status=status.HTTP_204_NO_CONTENT)
    if length > 100:
        actions = actions[length-100:]

    genre = {}
    dict1 = actions.values()
    for movie in dict1:
        gen = movie['genres']
        if gen in genre:
            genre[gen] += 1
        else:
            genre[gen] = 1
    li = []
    for i in genre.items():
        li.append(i)
    li.sort(key=lambda x : x[1], reverse=True)
    
    
    if len(li) == 1:
        num = list(range(1, 4))
        getNum = random.sample(num, 1)[0]
        if getNum == 1:     # 평점순 랜덤
            queryset = Movie.objects.filter(genres=li[0][0]).order_by('-vote_average').distinct()[:10]
        elif getNum == 2:   # 올 랜덤
            queryset = Movie.objects.filter(genres=li[0][0]).order_by('?')[:10]
        else:               # 최신영화 중에서 랜덤
            queryset = Movie.objects.filter(genres=li[0][0]).filter(release_date__range=[date.today() - timedelta(days=31), date.today()]).order_by('?')[:10]

    else:
        num = list(range(1, 4))
        getNum = random.sample(num, 1)[0]
        if getNum == 1:     # 평점순 랜덤
            queryset = Movie.objects.filter(genres__in=[li[0][0], li[1][0]]).order_by('-vote_average').distinct()[:10]
        elif getNum == 2:   # 올 랜덤
            movies = Movie.objects.filter(genres__in=[li[0][0], li[1][0]]).values('movie_id').order_by('-vote_average').distinct()
            random_movies = Movie.objects.filter(movie_id__in=movies)
            queryset = random.sample(list(random_movies), 10)
        else:               # 최신영화 중에서 랜덤
            movies = Movie.objects.filter(release_date__range=[date.today() - timedelta(days=365), date.today()]).filter(genres__in=[li[0][0], li[1][0]]).values('movie_id').order_by('-vote_average').distinct()
            random_movies = Movie.objects.filter(movie_id__in=movies)
            queryset = random.sample(list(random_movies), 10)
    serializer = MovieSerializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def movie_follow_like(request, user_id):
    User = get_user_model()
    user = User.objects.get(id=user_id) # 나의 정보
    my_like_movies = user.like_movies.all()
    following_people = user.followings.all()
    li = []

    # 내가 팔로우 한 사람들이 좋아하는 영화들의 집합
    for following in following_people:
        movies = following.like_movies.all()
        # print(movies)
        for movie in movies:
            if movie not in li:
                li.append(movie)
    # print(li)
    result = []
    for i in li:
        if i not in my_like_movies:
            result.append(i)
    if len(result) > 10:
        new_result = random.sample(result, 10)
    else:
        new_result = random.sample(result, len(result))

    serializer = MovieSerializer(new_result, many=True)
    # print(serializer.data)
    return Response(serializer.data)



@api_view(['GET'])
def cast_list(request, movie_pk):
    casts = get_list_or_404(Cast, movie_id=movie_pk)
    serializer = CastSerializer(casts, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_genre(request):
    genres = get_list_or_404(Genre)
    serializer = GenreListSerializer(genres, many=True)
    # print(serializer.data)
    return Response(serializer.data)


@api_view(['GET'])
def movie_like_list(request, username):
    User = get_user_model()
    user_id = User.objects.get(username=username).pk
    user = get_object_or_404(User, pk=user_id)
    movies = user.like_movies.all()
    serializer = MovieSerializer(movies, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def movie_search(request, inputData):
    movies = Movie.objects.filter(title__contains=inputData)
    movies = list(movies)
    casts = Cast.objects.filter(name__contains=inputData)
    
    for cast in casts:
        movie = Movie.objects.get(movie_id = cast.movie_id)
        if movie not in movies:
            movies.append(movie)

    # overview_movies = Movie.objects.filter(overview__contains=inputData)
    # for oveerview_movie in overview_movies:
    #     if oveerview_movie not in movies:
    #         movies.append(oveerview_movie) 
    # print(li)
    # print(list(movies) + li)
    
    serializer = MovieSerializer(movies, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def movie_related(request, movie_id):
    movie = Movie.objects.get(movie_id=movie_id)
    li = movie.genres.all()
    movies = Movie.objects.filter(recommend_movie_id=movie_id).order_by('?')[:6]
    if not(movies):
        if len(li) == 1:
            queryset = Movie.objects.filter(genres__in=[li[0]]).exclude(movie_id__in=[movie_id])
            movies = queryset.order_by('?')[:6]
        else:
            queryset = Movie.objects.filter(genres__in=[li[0],li[1]]).exclude(movie_id__in=[movie_id]).order_by('id').distinct()
            movies = set()
            for movie in queryset:
                if movie not in movies:
                    movies.add(movie)
            movies = random.sample(list(movies), 6)
    serializer = MovieSerializer(movies, many=True)
    # print(serializer)
    return Response(serializer.data)
    


@api_view(['GET'])
def movie_poster(request, movie_id):
    posters = get_list_or_404(Poster, movie_id = movie_id)
    serializer = PosterSerializer(posters, many=True)
    return Response(serializer.data)

# Create your views here.
# def get_movie_data(self):
#     # json 파일 불러오기
#     # 장르에 대한 정보 불러오기
#     genre_url = f'https://api.themoviedb.org/3/genre/movie/list?api_key=3595c601c2823fc7ada929e83ad9a293&language=ko-KR'
#     res2 = requests.get(genre_url)
#     other = res2.json()
#     # print(other['genres'])
#     for genre in other['genres']:
#         Genre.objects.create(
#                 name = genre['name'],
#                 pk = genre['id']
#             )

#     save = []
#     page = 1
#     # 페이지 설정
#     while page < 35:
#         # save 리스트에 영화 정보 저장
#         url = f'https://api.themoviedb.org/3/movie/top_rated?api_key=3595c601c2823fc7ada929e83ad9a293&page={page}&language=ko'
#         response = requests.get(url)
        
#         data = response.json()
#         save.extend(data['results'])
#         # print(save)
        
#         # 현재 상영작
#         url_upcoming = f'https://api.themoviedb.org/3/movie/upcoming?api_key=3595c601c2823fc7ada929e83ad9a293&language=ko-KR&page={page}'
#         response = requests.get(url_upcoming)
        
#         data_upcoming = response.json()
#         save.extend(data_upcoming['results'])
#         page += 1

    
#     total_movie_id = set()
#     # 각각의 영화 정보를 통해 배우 및 video link 추출
#     for row in save:
        
#         movie_id=row['id']
#         if movie_id in total_movie_id:
#             continue
#         total_movie_id.add(movie_id)
        
#         url_video = f'https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key=3595c601c2823fc7ada929e83ad9a293'
#         res = requests.get(url_video)
#         other_data = res.json()

#         video_url = 'http://www.youtube.com/embed/'
#         try:
#             video_url += other_data['results'][0]['key']
#         except:
#             # video link가 존재하지 않으면 넘어가기
#             continue
        
#         url_video_image = f'https://api.themoviedb.org/3/movie/{movie_id}/images?api_key=3595c601c2823fc7ada929e83ad9a293'
#         res = requests.get(url_video_image)
#         other_data_image = res.json()
#         image = []
#         i = 1
#         for other in other_data_image['backdrops']:
#             image.append(other)
            
#             i += 1
#             if i > 5:
#                 break
        
        
        
#         for i in image:
#             file_path = i['file_path']
#             image_url = f'https://www.themoviedb.org/t/p/original/{file_path}'
#             Poster.objects.create(
#                 movie_id=movie_id,
#                 file_path = image_url,
#             )
            
        
        
        
#         Movie.objects.create(
#         movie_id=row['id'],
#         title = row['title'],
#         poster_path = row['poster_path'],
#         release_date = row['release_date'],
#         overview = row['overview'],
#         video_path = video_url,
#         vote_average = row['vote_average'],
#         recommend_movie_id = 0,
#         )
#         movie = Movie.objects.get(movie_id=movie_id)
#         # print('######################################')
#         # print(movie)
        
#         provider_url = f'https://api.themoviedb.org/3/movie/{movie_id}/watch/providers?api_key=3595c601c2823fc7ada929e83ad9a293'
#         res_provider = requests.get(provider_url)
#         provider_data = res_provider.json()
#         try:
#             provider_link = provider_data['results']['KR']['link']
#             providers = provider_data['results']['KR']['flatrate']
#             for provider_logo_path in providers:
#                 path = provider_logo_path['logo_path']
#                 logo_path = f'https://www.themoviedb.org/t/p/original/{path}'
#                 Provider.objects.create(
#                     provider_link = provider_link,
#                     provider_logo_path = logo_path,
#                     movie = movie,
#                 )
#         except:
#             pass
        
        
#         for genre_id in row['genre_ids']:
#             genre = Genre.objects.get(id=genre_id)
#             movie = Movie.objects.get(movie_id= row['id'])
#             movie.genres.add(genre)


#         # 해당 영화의 배우 및 감독에 대한 정보
#         actor_url = f'https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key=3595c601c2823fc7ada929e83ad9a293&language=ko-KR'
#         res1 = requests.get(actor_url)
#         other_data1 = res1.json()
#         # print(other_data1['cast'])
        

#         for cast in other_data1['cast']:
#             cast_id = cast['id']
#             cast_url = f'https://www.themoviedb.org/person/{cast_id}?language=ko-KR'
#             Cast.objects.create(
#                 name = cast['name'],
#                 known_for_department = cast['known_for_department'],
#                 movie_id = other_data1['id'],
#                 credit_id = cast_url,
#             )
        
#         save_recommend = []
#         url_recommend = f'https://api.themoviedb.org/3/movie/{movie_id}/recommendations?api_key=3595c601c2823fc7ada929e83ad9a293&language=ko-KR&page=1'
#         response = requests.get(url_recommend)
        
#         data_recommend = response.json()
#         save_recommend.extend(data_recommend['results'])
#         # print(save)
        
#         #### 추천 영화 #####
#         for row in save_recommend:
#             movie_id_recommend=row['id']
#             if movie_id_recommend in total_movie_id:
#                 continue
#             total_movie_id.add(movie_id_recommend)
            
            
#             url_video = f'https://api.themoviedb.org/3/movie/{movie_id_recommend}/videos?api_key=3595c601c2823fc7ada929e83ad9a293'
#             res = requests.get(url_video)
#             other_data = res.json()

#             video_url = 'http://www.youtube.com/embed/'
#             try:
#                 video_url += other_data['results'][0]['key']
#             except:
#                 # video link가 존재하지 않으면 넘어가기
#                 continue
            
#             url_video_image = f'https://api.themoviedb.org/3/movie/{movie_id_recommend}/images?api_key=3595c601c2823fc7ada929e83ad9a293'
#             res = requests.get(url_video_image)
#             other_data_image = res.json()
#             image = []
#             i = 1
#             for other in other_data_image['backdrops']:
#                 image.append(other)
                
#                 i += 1
#                 if i > 5:
#                     break
            
#             for i in image:
#                 file_path = i['file_path']
#                 image_url = f'https://www.themoviedb.org/t/p/original/{file_path}'
#                 Poster.objects.create(
#                     movie_id=movie_id_recommend,
#                     file_path = image_url,
#                 )
                
            
#             Movie.objects.create(
#             movie_id=row['id'],
#             title = row['title'],
#             poster_path = row['poster_path'],
#             release_date = row['release_date'],
#             overview = row['overview'],
#             video_path = video_url,
#             vote_average = row['vote_average'],
#             recommend_movie_id = movie_id,
#             )
#             movie = Movie.objects.get(movie_id= row['id'])
            

            
#             provider_url = f'https://api.themoviedb.org/3/movie/{movie_id_recommend}/watch/providers?api_key=3595c601c2823fc7ada929e83ad9a293'
#             res_provider = requests.get(provider_url)
#             provider_data = res_provider.json()
#             try:
#                 provider_link = provider_data['results']['KR']['link']
#                 providers = provider_data['results']['KR']['flatrate']
#                 for provider_logo_path in providers:
#                     path = provider_logo_path['logo_path']
#                     logo_path = f'https://www.themoviedb.org/t/p/original/{path}'
#                     Provider.objects.create(
#                         provider_link = provider_link,
#                         provider_logo_path = logo_path,
#                         movie = movie,
#                     )
#             except:
#                 pass
            
            
            
            
            
#             for genre_id in row['genre_ids']:

#                 genre = Genre.objects.get(id=genre_id)
#                 movie = Movie.objects.get(movie_id= row['id'])
#                 movie.genres.add(genre)


#             # 해당 영화의 배우 및 감독에 대한 정보
#             actor_url = f'https://api.themoviedb.org/3/movie/{movie_id_recommend}/credits?api_key=3595c601c2823fc7ada929e83ad9a293&language=ko-KR'
#             res1 = requests.get(actor_url)
#             other_data1 = res1.json()
#             # print(other_data1['cast'])
            

#             for cast in other_data1['cast']:
#                 cast_id = cast['id']
#                 cast_url = f'https://www.themoviedb.org/person/{cast_id}?language=ko-KR'
#                 Cast.objects.create(
#                     name = cast['name'],
#                     known_for_department = cast['known_for_department'],
#                     movie_id = other_data1['id'],
#                     credit_id = cast_url,
#                 )
        
        
        

#     return HttpResponse('Success convert json to database')

