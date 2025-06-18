#!/usr/bin/env python
"""
Test script để kiểm tra các intent khác nhau của chatbot
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eatsndrinks.settings')
django.setup()

from chatbot.services import ChatbotService

def test_different_intents():
    """Test các intent khác nhau"""
    print("🧪 Testing Chatbot Intents")
    print("=" * 50)
    
    service = ChatbotService()
    
    # Test cases
    test_cases = [
        {
            'message': 'Xin chào',
            'expected_intent': 'greeting',
            'description': 'Chào hỏi cơ bản'
        },
        {
            'message': 'Hello',
            'expected_intent': 'greeting',
            'description': 'Chào hỏi tiếng Anh'
        },
        {
            'message': 'Tôi muốn tìm đồ uống',
            'expected_intent': 'search',
            'description': 'Tìm kiếm sản phẩm'
        },
        {
            'message': 'Đề xuất cho tôi món ăn ngon',
            'expected_intent': 'recommendation',
            'description': 'Yêu cầu đề xuất'
        },
        {
            'message': 'Có gì rẻ không?',
            'expected_intent': 'price_search',
            'description': 'Tìm sản phẩm rẻ'
        },
        {
            'message': 'Trang web này bán gì?',
            'expected_intent': 'general_question',
            'description': 'Hỏi chung về trang web'
        },
        {
            'message': 'Tôi muốn mua đồ uống có ga',
            'expected_intent': 'search',
            'description': 'Tìm kiếm cụ thể'
        },
        {
            'message': 'Có sản phẩm nào cao cấp không?',
            'expected_intent': 'price_search',
            'description': 'Tìm sản phẩm cao cấp'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['description']}")
        print(f"   Message: '{test_case['message']}'")
        
        # Analyze intent
        intent = service.analyze_user_intent(test_case['message'])
        print(f"   Detected Intent: {intent['intent']}")
        print(f"   Expected Intent: {test_case['expected_intent']}")
        
        # Test response
        result = service.process_chat(test_case['message'])
        print(f"   Response: {result['message']}")
        print(f"   Recommendations: {len(result['recommendations'])} sản phẩm")
        
        # Check if intent matches
        if intent['intent'] == test_case['expected_intent']:
            print("Intent detected correctly")
        else:
            print("Intent detection failed")
        
        print("-" * 40)

def test_greeting_no_recommendations():
    """Test rằng chào hỏi không recommend sản phẩm"""
    print("\n🎯 Testing Greeting - No Recommendations")
    print("=" * 50)
    
    service = ChatbotService()
    
    greeting_messages = [
        'Xin chào',
        'Hello',
        'Hi',
        'Chào bạn',
        'Xin chào bạn'
    ]
    
    for message in greeting_messages:
        print(f"\nTesting: '{message}'")
        result = service.process_chat(message)
        print(f"Response: {result['message']}")
        print(f"Recommendations: {len(result['recommendations'])} sản phẩm")
        
        if len(result['recommendations']) == 0:
            print("No recommendations (correct)")
        else:
            print("Has recommendations (incorrect)")

def test_search_with_recommendations():
    """Test rằng tìm kiếm có recommend sản phẩm"""
    print("\n🔍 Testing Search - With Recommendations")
    print("=" * 50)
    
    service = ChatbotService()
    
    search_messages = [
        'Tôi muốn tìm đồ uống',
        'Đề xuất cho tôi món ăn',
        'Có sản phẩm nào rẻ không?',
        'Tôi muốn mua thức ăn nhanh'
    ]
    
    for message in search_messages:
        print(f"\nTesting: '{message}'")
        result = service.process_chat(message)
        print(f"Response: {result['message']}")
        print(f"Recommendations: {len(result['recommendations'])} sản phẩm")
        
        if len(result['recommendations']) > 0:
            print("Has recommendations (correct)")
            for rec in result['recommendations'][:2]:  # Show first 2
                print(f"   - {rec['name']}: {rec['price']}đ")
        else:
            print("No recommendations (incorrect)")

def main():
    """Main function"""
    print("🤖 Chatbot Intent Testing")
    print("=" * 60)
    
    # Test different intents
    test_different_intents()
    
    # Test greeting behavior
    test_greeting_no_recommendations()
    
    # Test search behavior
    test_search_with_recommendations()
    
    print("\n" + "=" * 60)
    print("Testing completed!")
    print("\nKết quả mong đợi:")
    print("- Chào hỏi: Không recommend sản phẩm")
    print("- Tìm kiếm: Có recommend sản phẩm")
    print("- Intent detection: Chính xác")

if __name__ == "__main__":
    main() 