from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
def list_chats(request):
    """List chats endpoint"""
    return Response({'message': 'List chats endpoint'}, status=status.HTTP_200_OK)
