from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q

from .models import Event, RSVP, Review
from .serializers import EventSerializer, RSVPSerializer, ReviewSerializer
from .permissions import IsOrganizerOrReadOnly, IsInvitedOrPublic


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    # Allow read-only access to unauthenticated users (they can list/public view events).
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOrganizerOrReadOnly, IsInvitedOrPublic]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'location', 'organizer__username']

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Event.objects.filter(is_public=True)
        # Combine filters and remove duplicates
        qs = Event.objects.filter(is_public=True)
        qs = qs | Event.objects.filter(invited_users=user)
        qs = qs | Event.objects.filter(organizer=user)
        return qs.distinct().order_by('start_time')

    @action(detail=True, methods=['post'])
    def rsvp(self, request, pk=None):
        event = self.get_object()
        status_ = request.data.get('status', 'Going')
        rsvp, created = RSVP.objects.get_or_create(event=event, user=request.user)
        rsvp.status = status_
        rsvp.save()
        return Response(RSVPSerializer(rsvp).data)

    @action(detail=True, methods=['patch'], url_path=r'rsvp/(?P<user_id>[^/.]+)')
    def rsvp_update(self, request, pk=None, user_id=None):
        """Update RSVP for a specific user on this event. Only the RSVP owner or organizer may update."""
        event = self.get_object()
        try:
            target_user = event.organizer.__class__.objects.get(pk=user_id)
        except Exception:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                target_user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                return Response({'detail': 'user not found'}, status=status.HTTP_404_NOT_FOUND)

        # permission: only the RSVP owner or the event organizer can update
        if not (request.user == target_user or request.user == event.organizer):
            return Response({'detail': 'Not allowed'}, status=status.HTTP_403_FORBIDDEN)

        try:
            rsvp = RSVP.objects.get(event=event, user=target_user)
        except RSVP.DoesNotExist:
            return Response({'detail': 'RSVP not found'}, status=status.HTTP_404_NOT_FOUND)

        status_ = request.data.get('status')
        if status_:
            rsvp.status = status_
            rsvp.save()
        return Response(RSVPSerializer(rsvp).data)

    @action(detail=True, methods=['post'])
    def reviews(self, request, pk=None):
        event = self.get_object()
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(event=event, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def list_reviews(self, request, pk=None):
        event = self.get_object()
        reviews = Review.objects.filter(event=event)
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = ReviewSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)


class RSVPViewSet(viewsets.ModelViewSet):
    queryset = RSVP.objects.all()
    serializer_class = RSVPSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RSVP.objects.filter(user=self.request.user)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)
