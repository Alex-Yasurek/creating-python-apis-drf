from rest_framework import serializers
from todo.models import Todo


class TodoSerializer(serializers.ModelSerializer):

    created = serializers.ReadOnlyField()
    datecompleted = serializers.ReadOnlyField()

    class Meta:
        model = Todo
        fields = ['id', 'title', 'memo', 'created',
                  'datecompleted', 'important']


class TodoCompleteSerializer(serializers.ModelSerializer):
    """ Serializer for marking todo as complete. """
    # We dont want users updating anything in the todo, the system should
    # just add the date completed
    class Meta:
        model = Todo
        fields = ['id']
        read_only_fields = ['title', 'memo', 'created',
                            'datecompleted', 'important']
