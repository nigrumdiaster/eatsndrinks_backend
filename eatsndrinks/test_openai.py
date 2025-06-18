#!/usr/bin/env python
"""
Script để test OpenAI API key
"""

import os
import sys
import requests
import json
from decouple import config

def test_openai_api_key():
    """Test OpenAI API key"""
    print("🔑 Testing OpenAI API Key")
    print("=" * 50)
    
    # Lấy API key từ environment
    api_key = config('OPENAI_API_KEY', default='')
    
    if not api_key:
        print("❌ Không tìm thấy OPENAI_API_KEY trong file .env")
        print("\nHướng dẫn:")
        print("1. Tạo file .env trong thư mục eatsndrinks/")
        print("2. Thêm dòng: OPENAI_API_KEY=your-api-key-here")
        print("3. Chạy lại script này")
        return False
    
    print(f"✅ Tìm thấy API key: {api_key[:10]}...{api_key[-4:]}")
    
    # Test API call
    print("\n🧪 Testing API call...")
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {'role': 'user', 'content': 'Xin chào! Hãy trả lời ngắn gọn bằng tiếng Việt.'}
        ],
        'max_tokens': 50,
        'temperature': 0.7
    }
    
    try:
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            message = result['choices'][0]['message']['content']
            usage = result['usage']
            
            print("✅ API call thành công!")
            print(f"Response: {message}")
            print(f"Tokens used: {usage['total_tokens']}")
            print(f"Cost: ~${usage['total_tokens'] * 0.000002:.6f}")
            return True
            
        elif response.status_code == 401:
            print("❌ API key không hợp lệ hoặc đã hết hạn")
            print("Hãy kiểm tra lại API key của bạn")
            return False
            
        elif response.status_code == 429:
            print("❌ Rate limit exceeded")
            print("Bạn đã vượt quá giới hạn API calls")
            return False
            
        else:
            print(f"❌ Lỗi API: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Timeout - Kết nối quá chậm")
        return False
        
    except requests.exceptions.ConnectionError:
        print("❌ Không thể kết nối đến OpenAI API")
        print("Kiểm tra kết nối internet của bạn")
        return False
        
    except Exception as e:
        print(f"❌ Lỗi không xác định: {str(e)}")
        return False

def test_chatbot_with_openai():
    """Test chatbot với OpenAI"""
    print("\n🤖 Testing Chatbot with OpenAI")
    print("=" * 50)
    
    try:
        # Import Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eatsndrinks.settings')
        import django
        django.setup()
        
        from chatbot.services import ChatbotService
        
        service = ChatbotService()
        
        # Test với OpenAI
        test_messages = [
            "Xin chào",
            "Tôi muốn tìm đồ uống",
            "Đề xuất cho tôi món ăn ngon"
        ]
        
        for message in test_messages:
            print(f"\nTesting: '{message}'")
            result = service.process_chat(message)
            print(f"Response: {result['message']}")
            print(f"Model used: {result['metadata']['model_used']}")
            print(f"Recommendations: {len(result['recommendations'])} sản phẩm")
            
            if result['metadata']['model_used'] == 'gpt-3.5-turbo':
                print("✅ Sử dụng OpenAI GPT-3.5-turbo")
            else:
                print("⚠️ Sử dụng fallback mode")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khi test chatbot: {str(e)}")
        return False

def check_api_key_format():
    """Kiểm tra format của API key"""
    print("\n🔍 Checking API Key Format")
    print("=" * 50)
    
    api_key = config('OPENAI_API_KEY', default='')
    
    if not api_key:
        print("❌ Không có API key")
        return False
    
    # Kiểm tra format cơ bản
    if not api_key.startswith('sk-'):
        print("❌ API key không đúng format (phải bắt đầu bằng 'sk-')")
        return False
    
    if len(api_key) < 20:
        print("❌ API key quá ngắn")
        return False
    
    print("✅ API key có format hợp lệ")
    return True

def show_usage_info():
    """Hiển thị thông tin về usage"""
    print("\n📊 OpenAI API Usage Information")
    print("=" * 50)
    
    print("💰 Pricing (GPT-3.5-turbo):")
    print("- Input tokens: $0.0015 per 1K tokens")
    print("- Output tokens: $0.002 per 1K tokens")
    print("- Average cost per chat: ~$0.01-0.05")
    
    print("\n📈 Rate Limits:")
    print("- Free tier: 3 requests per minute")
    print("- Paid tier: 3,500 requests per minute")
    
    print("\n🔗 Useful Links:")
    print("- API Documentation: https://platform.openai.com/docs")
    print("- Usage Dashboard: https://platform.openai.com/usage")
    print("- API Keys: https://platform.openai.com/api-keys")

def main():
    """Main function"""
    print("🔑 OpenAI API Key Tester")
    print("=" * 60)
    
    # Kiểm tra format
    format_ok = check_api_key_format()
    
    if format_ok:
        # Test API
        api_ok = test_openai_api_key()
        
        if api_ok:
            # Test chatbot
            chatbot_ok = test_chatbot_with_openai()
            
            if chatbot_ok:
                print("\n🎉 Tất cả tests đều thành công!")
                print("Chatbot sẽ sử dụng OpenAI GPT-3.5-turbo")
            else:
                print("\n⚠️ API key hoạt động nhưng chatbot có vấn đề")
        else:
            print("\n❌ API key không hoạt động")
            print("Chatbot sẽ sử dụng fallback mode")
    else:
        print("\n❌ API key không đúng format")
    
    # Hiển thị thông tin usage
    show_usage_info()
    
    print("\n" + "=" * 60)
    print("✅ Testing completed!")

if __name__ == "__main__":
    main() 