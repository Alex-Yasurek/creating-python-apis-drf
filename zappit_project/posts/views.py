from rest_framework.exceptions import ValidationError
from rest_framework import generics, permissions, mixins, status
from rest_framework.response import Response
from .models import Post, Vote
from .serializers import PostSerializer, VoteSerializer


# Creating and listing posts
class PostList(generics.ListCreateAPIView):
    # queryset = what are we pulling from database
    queryset = Post.objects.all()
    # serializer to transform data from model to json and vice versa
    serializer_class = PostSerializer
    # sets permission so that to use POST/PUT you have to be signed in
    # but to use GET you can be anonymous
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # make user making api call the poster
        serializer.save(poster=self.request.user)


# viewing and deleting posts
class PostRetrieveDestroy(generics.RetrieveDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def delete(self, request, *args, **kwargs):
        # check it was their post they want to delete
        post = Post.objects.filter(
            pk=self.kwargs['pk'], poster=self.request.user)
        if post.exists():
            return self.destroy(request, *args, **kwargs)
        else:
            raise ValidationError('You did not create this post.')


# Adding votes to posts
class VoteCreate(generics.CreateAPIView, mixins.DestroyModelMixin):
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # define what gets returned when making GET request
        user = self.request.user
        post = Post.objects.get(pk=self.kwargs['pk'])
        return Vote.objects.filter(voter=user, post=post)

    def perform_create(self, serializer):
        # before adding vote, make sure they havent voted already
        if self.get_queryset().exists():
            raise ValidationError('You have already voted for this post.')
        serializer.save(voter=self.request.user,
                        post=Post.objects.get(pk=self.kwargs['pk']))

    def delete(self, request, *args, **kwargs):
        # check vote exists first
        if self.get_queryset().exists():
            self.get_queryset().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationError('You never voted for this post.')
