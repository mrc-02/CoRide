from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
def list_rides(request):
    """List rides endpoint"""
    return Response({'message': 'List rides endpoint'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def create_ride(request):
    """Create ride endpoint"""
    return Response({'message': 'Create ride endpoint'}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def ride_detail(request, rid):
    """Get ride detail endpoint"""
    return Response({'message': 'Ride detail endpoint'}, status=status.HTTP_200_OK)
