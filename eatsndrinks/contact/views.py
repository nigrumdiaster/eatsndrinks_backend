from django.shortcuts import render
from rest_framework import serializers, viewsets, permissions
from .serializers import ContactSerializer
from .models import Contact
from rest_framework.permissions import IsAdminUser
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from .models import Contact
# Create your views here.
class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all().order_by('-created_at')
    serializer_class = ContactSerializer
    permission_classes = [IsAdminUser]  # Change as needed

    def perform_create(self, serializer):
        serializer.save()

@api_view(['POST'])
@permission_classes([IsAdminUser])
def reply_to_contact(request):
    contact_id = request.data.get('contact_id')
    reply_html = request.data.get('message')  # Nội dung CKEditor

    try:
        contact = Contact.objects.get(id=contact_id)
        
        # Gửi email với nội dung HTML
        subject = "Reply to Your Inquiry"
        text_content = strip_tags(reply_html)  # Loại bỏ HTML cho phiên bản text
        msg = EmailMultiAlternatives(subject, text_content, "noreply@example.com", [contact.email])
        msg.attach_alternative(reply_html, "text/html")
        msg.send()

        # Cập nhật trạng thái đã trả lời
        contact.is_replied = True
        contact.save()

        return Response({'success': 'Reply sent successfully!'}, status=200)
    except Contact.DoesNotExist:
        return Response({'error': 'Message not found'}, status=404)