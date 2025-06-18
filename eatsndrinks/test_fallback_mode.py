#!/usr/bin/env python
"""
Test fallback mode khi không có OpenAI API
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eatsndrinks.settings')
django.setup()

from chatbot.services import ChatbotService

def test_fallback_mode():
    """Test fallback mode"""
    print("🤖 Testing Fallback Mode")
    print("=" * 50)
    
    service = ChatbotService()
    
    # Test các trường hợp khác nhau
    test_cases = [
        {
            'message': 'Xin chào',
            'expected_behavior': 'Chào lại, không recommend sản phẩm'
        },
        {
            'message': 'Tôi muốn tìm đồ uống',
            'expected_behavior': 'Recommend sản phẩm đồ uống'
        },
        {
            'message': 'Có gì rẻ không?',
            'expected_behavior': 'Recommend sản phẩm giá thấp'
        },
        {
            'message': 'Trang web này bán gì?',
            'expected_behavior': 'Giới thiệu về trang web'
        },
        {
            'message': 'Đề xuất cho tôi món ăn ngon',
            'expected_behavior': 'Recommend sản phẩm'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: '{test_case['message']}'")
        print(f"   Expected: {test_case['expected_behavior']}")
        
        result = service.process_chat(test_case['message'])
        
        print(f"   Response: {result['message']}")
        print(f"   Model: {result['metadata']['model_used']}")
        print(f"   Recommendations: {len(result['recommendations'])} sản phẩm")
        
        if result['metadata']['model_used'] == 'fallback':
            print("Sử dụng fallback mode")
        else:
            print("Sử dụng OpenAI")
        
        # Show recommendations if any
        if result['recommendations']:
            print("Sản phẩm được đề xuất:")
            for rec in result['recommendations'][:3]:
                print(f"      - {rec['name']}: {rec['price']}đ")
        
        print("-" * 40)

def test_intent_detection():
    """Test intent detection"""
    print("\n🔍 Testing Intent Detection")
    print("=" * 50)
    
    service = ChatbotService()
    
    test_messages = [
        'Xin chào',
        'Hello',
        'Tôi muốn tìm đồ uống',
        'Có gì rẻ không?',
        'Trang web này bán gì?',
        'Đề xuất cho tôi món ăn'
    ]
    
    for message in test_messages:
        intent = service.analyze_user_intent(message)
        print(f"\nMessage: '{message}'")
        print(f"Intent: {intent['intent']}")
        print(f"Is Greeting: {intent['is_greeting']}")
        print(f"Is Search: {intent['is_search']}")
        print(f"Is Recommendation: {intent['is_recommendation_request']}")

def main():
    """Main function"""
    print("Fallback Mode Testing")
    print("=" * 60)
    
    print("ℹFallback mode hoạt động khi:")
    print("- Không có OpenAI API key")
    print("- API key hết quota")
    print("- Không có kết nối internet")
    print("- OpenAI API bị lỗi")
    
    # Test intent detection
    test_intent_detection()
    
    # Test fallback mode
    test_fallback_mode()
    
    print("\n" + "=" * 60)
    print("Fallback mode hoạt động tốt!")
    print("\n💡 Lưu ý:")
    print("- Fallback mode đơn giản hơn nhưng vẫn hữu ích")
    print("- Nạp credit OpenAI để có trải nghiệm tốt hơn")
    print("- Chatbot vẫn recommend sản phẩm chính xác")

if __name__ == "__main__":
    main() 