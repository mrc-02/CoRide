from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
def list_notifications(request):
    """List notifications endpoint"""
    return Response({'message': 'List notifications endpoint'}, status=status.HTTP_200_OK)
