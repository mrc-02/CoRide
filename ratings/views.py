from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
def list_ratings(request):
    """List ratings endpoint"""
    return Response({'message': 'List ratings endpoint'}, status=status.HTTP_200_OK)
