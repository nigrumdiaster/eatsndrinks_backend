from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from .serializers import (
    ChatRequestSerializer, 
    ChatResponseSerializer, 
    ChatSessionSerializer,
    ChatMessageSerializer,
    ChatbotConfigSerializer
)
from .services import ChatbotService
from .models import ChatSession, ChatMessage, ChatbotConfig

# Create your views here.

@extend_schema(
    tags=['Chatbot'],
    summary='Chat với chatbot',
    description='Gửi tin nhắn đến chatbot và nhận phản hồi với đề xuất sản phẩm',
    request=ChatRequestSerializer,
    responses={
        200: ChatResponseSerializer,
        400: None,
    },
    examples=[
        OpenApiExample(
            'Chat Example',
            value={
                'message': 'Tôi muốn tìm đồ uống',
                'session_id': 'optional-session-id'
            },
            request_only=True
        ),
        OpenApiExample(
            'Response Example',
            value={
                'message': 'Tôi có thể giúp bạn tìm đồ uống! Dưới đây là một số gợi ý:',
                'session_id': 'session-123',
                'recommendations': [
                    {
                        'product': {
                            'id': 1,
                            'name': 'Coca Cola',
                            'price': '25000.00',
                            'description': 'Nước ngọt Coca Cola'
                        },
                        'confidence_score': 0.8,
                        'reason': 'Được đề xuất bởi chatbot'
                    }
                ],
                'metadata': {
                    'model_used': 'gpt-3.5-turbo',
                    'tokens_used': 150
                }
            },
            response_only=True
        )
    ]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def chat(request):
    """
    Chat với chatbot để nhận đề xuất sản phẩm
    """
    serializer = ChatRequestSerializer(data=request.data)
    if serializer.is_valid():
        message = serializer.validated_data['message']
        session_id = serializer.validated_data.get('session_id')
        user_id = serializer.validated_data.get('user_id')
        
        # Process chat
        chatbot_service = ChatbotService()
        result = chatbot_service.process_chat(message, session_id, user_id)
        
        # Prepare response
        response_data = {
            'message': result['message'],
            'session_id': result['session_id'],
            'recommendations': result['recommendations'],
            'metadata': result['metadata']
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    tags=['Chatbot'],
    summary='Lấy lịch sử chat',
    description='Lấy lịch sử tin nhắn của một session chat',
    parameters=[
        OpenApiParameter(name='session_id', type=str, location=OpenApiParameter.QUERY, required=True),
        OpenApiParameter(name='limit', type=int, location=OpenApiParameter.QUERY, default=20),
    ],
    responses={
        200: ChatMessageSerializer(many=True),
        404: None,
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def chat_history(request):
    """
    Lấy lịch sử chat của một session
    """
    session_id = request.query_params.get('session_id')
    limit = int(request.query_params.get('limit', 20))
    
    if not session_id:
        return Response({'error': 'session_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        session = ChatSession.objects.get(session_id=session_id)
        messages = ChatMessage.objects.filter(session=session).order_by('-timestamp')[:limit]
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ChatSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

@extend_schema(
    tags=['Chatbot'],
    summary='Tạo session chat mới',
    description='Tạo một session chat mới',
    responses={
        201: ChatSessionSerializer,
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def create_session(request):
    """
    Tạo session chat mới
    """
    chatbot_service = ChatbotService()
    session = chatbot_service.get_or_create_session()
    serializer = ChatSessionSerializer(session)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@extend_schema(
    tags=['Chatbot'],
    summary='Lấy cấu hình chatbot',
    description='Lấy cấu hình hiện tại của chatbot',
    responses={
        200: ChatbotConfigSerializer,
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_config(request):
    """
    Lấy cấu hình chatbot
    """
    try:
        config = ChatbotConfig.objects.filter(is_active=True).first()
        if config:
            serializer = ChatbotConfigSerializer(config)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'No active configuration found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(
    tags=['Chatbot'],
    summary='Đề xuất sản phẩm nhanh',
    description='Nhận đề xuất sản phẩm dựa trên từ khóa',
    parameters=[
        OpenApiParameter(name='keyword', type=str, location=OpenApiParameter.QUERY, required=True),
        OpenApiParameter(name='limit', type=int, location=OpenApiParameter.QUERY, default=5),
    ],
    responses={
        200: None,
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def quick_recommendations(request):
    """
    Đề xuất sản phẩm nhanh dựa trên từ khóa
    """
    keyword = request.query_params.get('keyword')
    limit = int(request.query_params.get('limit', 5))
    
    if not keyword:
        return Response({'error': 'keyword is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    chatbot_service = ChatbotService()
    intent_analysis = chatbot_service.analyze_user_intent(keyword)
    recommendations = chatbot_service.get_recommendations(intent_analysis, limit)
    
    # Convert to simple format
    products_data = []
    for product in recommendations:
        products_data.append({
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': float(product.current_price()),
            'category': product.category.name if product.category else 'Uncategorized',
            'is_flash_sale': product.is_flash_sale_active(),
            'flash_sale_price': float(product.flash_sale_price) if product.flash_sale_price else None,
        })
    
    return Response({
        'keyword': keyword,
        'recommendations': products_data,
        'total_found': len(products_data)
    }, status=status.HTTP_200_OK)
