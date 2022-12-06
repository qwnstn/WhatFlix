from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.shortcuts import get_object_or_404, get_list_or_404
from .serializers import ReviewSerializer, CommentSerializer
from .models import Review, Comment
from movies.models import Movie

# Create your views here.


@api_view(['GET', 'POST'])
def review_list(request, movie_id):
    if request.method == 'GET':
        reviews = get_list_or_404(Review, movie_id=movie_id)
        serializer = ReviewSerializer(reviews, many=True)
        # print(reviews)
        cnt = 0
        total_rank = 0
        for review in reviews:
            cnt += 1
            total_rank += review.rank
        # print(cnt, total_rank)
        average_rank = round(total_rank / cnt, 2)
        return Response({'serializer': serializer.data, 'average_rank': average_rank})
    elif request.method=="POST":
        movie = get_object_or_404(Movie, pk=movie_id)
        user = request.user
        review = Review.objects.all().filter(movie_id=movie_id, review_user=user)
        if review:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            serializer = ReviewSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(review_user= request.user)
                serializer.save(movie=movie)
                return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
def comment_list(request, review_id):
    if request.method == 'GET':
        comments = get_list_or_404(Comment, review=review_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data) 
    elif request.method == "POST":
        review = get_object_or_404(Review, pk=review_id)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(review= review)
            serializer.save(comment_user= request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
@api_view(['GET', 'POST'])
def review_like(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    user = request.user
    if request.method == 'GET':
        if user in review.like_users.all():
            data = {'liked': True}
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {'liked': False}
            return Response(data, status=status.HTTP_200_OK)
            
    elif request.method == 'POST':
        if user in review.like_users.all():
            review.like_users.remove(user)
            data={'liked': False}
            return Response(data ,status=status.HTTP_204_NO_CONTENT)
        else:
            review.like_users.add(user)
            data={'liked': True}
            return Response(data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def review_profile(request, review_user_id):
    user = request.user
    reviews = get_list_or_404(Review, review_user= review_user_id)
    li = []
    for review in reviews:
        serializer = ReviewSerializer(review)
        movie_title = review.movie.title
        movie_poster_path = review.movie.poster_path
        movie_id = review.movie.movie_id
        li.append({'serializer': serializer.data, 'movie_id' : movie_id,'movie_title' : movie_title, 'movie_poster_path' : movie_poster_path})
    return Response(li)


@api_view(['GET', 'DELETE', 'PUT'])
def review_detail(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    user = request.user
    if request.method == 'GET':
        serializer = ReviewSerializer(review)
        return Response(serializer.data)
    elif request.method == 'DELETE':
        if user == review.review_user:
            review.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
    elif request.method == 'PUT':
        if user == review.review_user:
            serializer = ReviewSerializer(review, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET', 'DELETE', 'PUT'])
def comment_detail(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    user = request.user
    if request.method == 'GET':
        serializer = CommentSerializer(comment)
        return Response(serializer.data)
    elif request.method == 'DELETE':
        if user == comment.comment_user:
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
    elif request.method == 'PUT':
        if user == comment.comment_user:
            serializer = CommentSerializer(comment, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)