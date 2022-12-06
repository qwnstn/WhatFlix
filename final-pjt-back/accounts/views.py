from django.shortcuts import get_object_or_404, get_list_or_404
from django.http import HttpResponse, JsonResponse, FileResponse

from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth import get_user_model
from .models import User
from rest_framework import status
from .serializers import UserSerializer
from .forms import UserForm
import random
import shutil
# Create your views here.

# @api_view(['GET'])
# def default_image(request):
#     ran = random.sample(range(1, 5), 1)
#     image = 'default' + str(ran)
#     img = open(f'media/defaults/{image}.png', 'rb')
#     response = FileResponse(img)
#     return response


@api_view(['GET', 'POST', 'DELETE'])
def profile_image(request, user_id):
    User = get_user_model()
    me = request.user
    person = User.objects.get(id=user_id)
    if request.method == 'GET':
        if person.profile_image:
            serializer = UserSerializer(person)
        else:
            ran = random.sample(range(0, 4), 1)
            image = './media/defaults/default' + str(ran[0]) + '.png'
            shutil.copy(image, './media/images/default'+ str(ran[0]) + person.username + '.png')
            person.profile_image = 'images/default'+ str(ran[0]) + person.username + '.png'
            person.save()
            serializer = UserSerializer(person)
        return Response(serializer.data)
    elif request.method == 'POST':
        if me == person:
            person.profile_image.delete()
            form = UserForm(request.POST, request.FILES, instance=person)
            # print(form.is_valid())
            # print(request.FILES.get('image'))
            if form.is_valid():
                form = form.save(commit=False)
                form.profile_image=request.FILES.get('image')
                form.save()
                # print(form)
            serializer = UserSerializer(person)
            return Response(serializer.data)
    elif request.method == 'DELETE':
        person.profile_image.delete()
        ran = random.sample(range(0, 4), 1)
        image = './media/defaults/default' + str(ran[0]) + '.png'
        # shutil.copy(image, './media/images/default'+ str(ran[0]) + '.png')
        # person.profile_image = 'images/default'+ str(ran[0]) + '.png'
        shutil.copy(image, './media/images/default'+ str(ran[0]) + person.username + '.png')
        person.profile_image = 'images/default'+ str(ran[0]) + person.username + '.png'
        person.save()
        serializer = UserSerializer(person)
        return Response(serializer.data)
    
# 유저 pk 입력 시 username 반환 기능
# data: {userid: userid}
# headers: {Authorization: Token {token}}
@api_view(['POST'])
def wantname(request):
    Userid = request.user
    if request.method == 'POST':
        user = Userid.id
        userid = request.data['userid']
        username = User.objects.get(pk = userid).username
        return JsonResponse({'username': username, 'userid': user})

# username 입력 시 유저 pk 반환 기능
# data: {username: username}
# headers: {Authorization: Token {token}}
@api_view(['POST'])
def wantid(request):
    if request.method == 'POST':
        username = request.data['username']
        userid = User.objects.get(username = username).pk
        return JsonResponse({'userid': userid})

# 회원 탈퇴
@api_view(['POST'])
def leave(request):
    if request.method == 'POST':
        user = request.user
        # user.is_active = False
        # user.save()
        user.delete()
        return HttpResponse('OK')

# 팔로우
@api_view(['GET', 'POST'])
def follow(request, user_pk):
    person = get_object_or_404(get_user_model(), pk=user_pk)    # you
    user = request.user                                         # me
    if person != user:
        if request.method == 'GET':
            if person.followers.filter(pk=user.pk).exists():
                return Response(True, status=status.HTTP_201_CREATED)
            else:
                return Response(False, status=status.HTTP_204_NO_CONTENT)
        elif request.method == 'POST':
            if person.followers.filter(pk=user.pk).exists():
                person.followers.remove(user)
                return Response(False, status=status.HTTP_204_NO_CONTENT)
            else:
                person.followers.add(user)
                return Response(True, status=status.HTTP_201_CREATED)
    return HttpResponse('NO')


@api_view(['GET'])
def following_profile(request, user_pk):
    User = get_user_model()
    person = User.objects.get(pk=user_pk)
    followings = person.followings.all()
    serializer = UserSerializer(followings, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def follower_profile(request, user_pk):
    User = get_user_model()
    person = User.objects.get(pk=user_pk)
    followers = person.followers.all()
    serializer = UserSerializer(followers, many=True)
    return Response(serializer.data)



# 팔로워 수 세기
@api_view(['GET'])
def followcount(request, user_pk):
    person = get_object_or_404(get_user_model(), pk=user_pk)
    context = {
        'followers_count': person.followers.count(),
        'followings_count': person.followings.count(),
    }
    # print(person.followers.count())
    # print(person.followings.count())
    return JsonResponse(context)