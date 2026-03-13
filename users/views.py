from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
def list_users(request):
    """List users endpoint"""
    return Response({'message': 'List users endpoint'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def user_profile(request):
    """Get user profile endpoint"""
    return Response({'message': 'User profile endpoint'}, status=status.HTTP_200_OK)
