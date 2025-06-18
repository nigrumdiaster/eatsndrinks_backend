from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import ChatSession, ChatMessage, ProductRecommendation, ChatbotConfig
from catalogue.models import Category, Product
from users.models import User
import json

class ChatbotModelsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.category = Category.objects.create(
            name='Đồ uống',
            description='Các loại đồ uống'
        )
        
        self.product = Product.objects.create(
            name='Coca Cola',
            description='Nước ngọt Coca Cola',
            price=25000.00,
            category=self.category
        )
    
    def test_chat_session_creation(self):
        session = ChatSession.objects.create(
            user=self.user,
            session_id='test-session-123'
        )
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.session_id, 'test-session-123')
        self.assertTrue(session.is_active)
    
    def test_chat_message_creation(self):
        session = ChatSession.objects.create(session_id='test-session-123')
        message = ChatMessage.objects.create(
            session=session,
            message_type='user',
            content='Tôi muốn tìm đồ uống'
        )
        self.assertEqual(message.session, session)
        self.assertEqual(message.message_type, 'user')
        self.assertEqual(message.content, 'Tôi muốn tìm đồ uống')
    
    def test_product_recommendation_creation(self):
        session = ChatSession.objects.create(session_id='test-session-123')
        message = ChatMessage.objects.create(
            session=session,
            message_type='bot',
            content='Đây là đề xuất cho bạn'
        )
        
        recommendation = ProductRecommendation.objects.create(
            message=message,
            product=self.product,
            confidence_score=0.8,
            reason='Được đề xuất bởi chatbot'
        )
        
        self.assertEqual(recommendation.message, message)
        self.assertEqual(recommendation.product, self.product)
        self.assertEqual(recommendation.confidence_score, 0.8)

class ChatbotAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.category = Category.objects.create(
            name='Đồ uống',
            description='Các loại đồ uống'
        )
        
        self.product = Product.objects.create(
            name='Coca Cola',
            description='Nước ngọt Coca Cola',
            price=25000.00,
            category=self.category
        )
    
    def test_chat_endpoint(self):
        """Test chat endpoint"""
        url = reverse('chatbot:chat')
        data = {
            'message': 'Tôi muốn tìm đồ uống'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check response structure
        self.assertIn('message', response.data)
        self.assertIn('session_id', response.data)
        self.assertIn('recommendations', response.data)
        self.assertIn('metadata', response.data)
    
    def test_create_session_endpoint(self):
        """Test create session endpoint"""
        url = reverse('chatbot:create_session')
        
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check response structure
        self.assertIn('session_id', response.data)
        self.assertIn('created_at', response.data)
        self.assertIn('is_active', response.data)
    
    def test_chat_history_endpoint(self):
        """Test chat history endpoint"""
        # Create a session and some messages first
        session = ChatSession.objects.create(session_id='test-session-123')
        ChatMessage.objects.create(
            session=session,
            message_type='user',
            content='Test message'
        )
        
        url = reverse('chatbot:chat_history')
        response = self.client.get(url, {'session_id': 'test-session-123'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], 'Test message')
    
    def test_quick_recommendations_endpoint(self):
        """Test quick recommendations endpoint"""
        url = reverse('chatbot:quick_recommendations')
        response = self.client.get(url, {'keyword': 'đồ uống'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('keyword', response.data)
        self.assertIn('recommendations', response.data)
        self.assertIn('total_found', response.data)
    
    def test_chat_with_session_id(self):
        """Test chat with existing session ID"""
        # Create a session first
        session = ChatSession.objects.create(session_id='existing-session-123')
        
        url = reverse('chatbot:chat')
        data = {
            'message': 'Tôi muốn tìm đồ uống',
            'session_id': 'existing-session-123'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['session_id'], 'existing-session-123')
    
    def test_chat_without_message(self):
        """Test chat endpoint with missing message"""
        url = reverse('chatbot:chat')
        data = {}
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_chat_history_without_session_id(self):
        """Test chat history without session ID"""
        url = reverse('chatbot:chat_history')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_chat_history_with_invalid_session_id(self):
        """Test chat history with invalid session ID"""
        url = reverse('chatbot:chat_history')
        response = self.client.get(url, {'session_id': 'invalid-session'})
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
