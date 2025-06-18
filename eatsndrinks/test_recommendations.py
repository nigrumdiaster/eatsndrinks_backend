#!/usr/bin/env python
"""
Test recommendations với OpenAI
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eatsndrinks.settings')
django.setup()

from chatbot.services import ChatbotService

def test_recommendations():
    """Test recommendations"""
    print("🎯 Testing Recommendations with OpenAI")
    print("=" * 50)
    
    service = ChatbotService()
    
    # Test cases
    test_cases = [
        {
            'message': 'Tôi muốn tìm đồ uống',
            'expected': 'Should recommend drinks'
        },
        {
            'message': 'Đề xuất cho tôi món ăn ngon',
            'expected': 'Should recommend food'
        },
        {
            'message': 'Có gì rẻ không?',
            'expected': 'Should recommend cheap products'
        },
        {
            'message': 'Tôi muốn mua Milo',
            'expected': 'Should mention Milo'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: '{test_case['message']}'")
        print(f"   Expected: {test_case['expected']}")
        
        result = service.process_chat(test_case['message'])
        
        print(f"   Model: {result['metadata']['model_used']}")
        print(f"   Response: {result['message'][:100]}...")
        print(f"   Recommendations: {len(result['recommendations'])} sản phẩm")
        
        if result['recommendations']:
            print("   📦 Sản phẩm được đề xuất:")
            for rec in result['recommendations']:
                print(f"      - {rec['name']}: {rec['price']}đ")
        else:
            print("   ⚠️ Không có recommendations")
        
        print("-" * 40)

def test_greeting_no_recommendations():
    """Test rằng chào hỏi không recommend sản phẩm"""
    print("\n🎯 Testing Greeting - No Recommendations")
    print("=" * 50)
    
    service = ChatbotService()
    
    greeting_messages = [
        'Xin chào',
        'Hello',
        'Hi'
    ]
    
    for message in greeting_messages:
        print(f"\nTesting: '{message}'")
        result = service.process_chat(message)
        print(f"Model: {result['metadata']['model_used']}")
        print(f"Response: {result['message'][:50]}...")
        print(f"Recommendations: {len(result['recommendations'])} sản phẩm")
        
        if len(result['recommendations']) == 0:
            print("✅ No recommendations (correct)")
        else:
            print("❌ Has recommendations (incorrect)")

def main():
    """Main function"""
    print("🎯 Recommendations Testing")
    print("=" * 60)
    
    # Test recommendations
    test_recommendations()
    
    # Test greeting behavior
    test_greeting_no_recommendations()
    
    print("\n" + "=" * 60)
    print("✅ Testing completed!")

if __name__ == "__main__":
    main() 