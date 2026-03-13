from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
def login(request):
    """Login endpoint"""
    return Response({'message': 'Login endpoint'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def register(request):
    """Register endpoint"""
    return Response({'message': 'Register endpoint'}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def logout(request):
    """Logout endpoint"""
    return Response({'message': 'Logout endpoint'}, status=status.HTTP_200_OK)
