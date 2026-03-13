from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
def list_drivers(request):
    """List drivers endpoint"""
    return Response({'message': 'List drivers endpoint'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def register_driver(request):
    """Register driver endpoint"""
    return Response({'message': 'Register driver endpoint'}, status=status.HTTP_201_CREATED)
