from django.shortcuts import render
from rest_framework import serializers, viewsets, permissions
from .serializers import ContactSerializer
from .models import Contact
from rest_framework.permissions import IsAdminUser
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.views import APIView
from .models import Contact
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
# Create your views here.
class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all().order_by('-created_at')
    serializer_class = ContactSerializer

    def get_permissions(self):
        if self.action == "create":  # Nếu là POST (tạo contact), cho phép tất cả
            return [AllowAny()]
        return [IsAdminUser()]  # Các hành động khác chỉ cho Admin

@method_decorator(csrf_exempt, name="dispatch")
class ReplyToContactView(APIView):
    permission_classes = [IsAdminUser]


    @extend_schema(
        summary="Reply to a contact message",
        description="Send an email reply to a contact message",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "contact_id": {"type": "integer", "example": 1},
                    "subject": {"type": "string", "example": "Thank you for reaching out"},
                    "message": {"type": "string", "example": "<h3>Hello!</h3><p>Thank you for reaching out to us.</p>"}
                },
                "required": ["contact_id", "subject", "message"]
            }
        },
        responses={
            200: {"description": "Reply sent successfully", "content": {"application/json": {"example": {"success": "Reply sent successfully!"}}}},
            404: {"description": "Message not found", "content": {"application/json": {"example": {"error": "Message not found"}}}}
        },
    )
    def post(self, request, *args, **kwargs):
        contact_id = request.data.get("contact_id")
        subject = request.data.get("subject")
        reply_html = request.data.get("message")

        try:
            contact = Contact.objects.get(id=contact_id)
            # Gửi email phản hồi
            text_content = strip_tags(reply_html)  # Loại bỏ HTML để tạo phiên bản text
            from_email = "Support Team <noreply@eatsndrinks.com>"
            msg = EmailMultiAlternatives(
                subject, text_content, from_email, [contact.email]
            )
            msg.attach_alternative(reply_html, "text/html")
            msg.send()

            # Cập nhật trạng thái đã trả lời
            contact.is_replied = True
            contact.save()

            return Response({"success": "Reply sent successfully!"}, status=200)
        except Contact.DoesNotExist:
            return Response({"error": "Message not found"}, status=404)
