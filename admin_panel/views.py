from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
def admin_dashboard(request):
    """Admin dashboard endpoint"""
    return Response({'message': 'Admin dashboard endpoint'}, status=status.HTTP_200_OK)
