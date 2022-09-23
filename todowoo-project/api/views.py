from django.utils import timezone
from rest_framework import generics, permissions
from .serializers import TodoSerializer, TodoCompleteSerializer
from todo.models import Todo
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http import JsonResponse
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

# exempt func from csrf checking
@csrf_exempt
def signup(request):
    if request.method == 'POST':
        try:
            # get data from request
            data = JSONParser().parse(request)
            user = User.objects.create_user(
                data['username'], password=data['password'])
            user.save()
            login(request, user)
            # use token model to create a token
            token = Token.objects.create(user=user)
            return JsonResponse({'token': str(token)}, status=201)
        except IntegrityError:
            return JsonResponse({'error': 'That username has already been taken. Please choose a new username'}, status=400)


@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        user = authenticate(
            request, username=data['username'], password=data['password'])
        if user is None:
            return JsonResponse({'error': 'Could not login. Please check username/password'}, status=400)
        else:
            try:
                token = Token.objects.get(user=user)
            except:
                token = Token.objects.create(user=user)
            return JsonResponse({'token': str(token)}, status=200)


class TodoCompletedList(generics.ListAPIView):
    # define serializer to us
    serializer_class = TodoSerializer
    # define permissions needed to acces this api
    permission_classes = [permissions.IsAuthenticated]

    # define what should be returned when api is called
    def get_queryset(self):
        # get user making request
        user = self.request.user
        # only return todos by user making call and that are completed
        return Todo.objects.filter(user=user, datecompleted__isnull=False).order_by('-datecompleted')


class TodoListCreate(generics.ListCreateAPIView):
    serializer_class = TodoSerializer
    permission_classes = [permissions.IsAuthenticated]

    # define what should be returned when api is called
    def get_queryset(self):
        # get user making request
        user = self.request.user
        # only return todos by user making call and that are not
        # completed
        return Todo.objects.filter(user=user, datecompleted__isnull=True)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TodoRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TodoSerializer
    permission_classes = [permissions.IsAuthenticated]

    # define what should be returned when api is called
    def get_queryset(self):
        # get user making request
        user = self.request.user
        # only return todos by user making call
        return Todo.objects.filter(user=user)


class TodoComplete(generics.UpdateAPIView):
    serializer_class = TodoCompleteSerializer
    permission_classes = [permissions.IsAuthenticated]

    # define what should be returned when api is called
    def get_queryset(self):
        # get user making request
        user = self.request.user
        # only return todos by user making call
        return Todo.objects.filter(user=user)

    # define what happens on udpate
    def perform_update(self, serializer):
        # just update the date completed field
        serializer.instance.datecompleted = timezone.now()
        serializer.save()
