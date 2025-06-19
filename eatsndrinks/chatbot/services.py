import json
import uuid
from typing import List, Dict, Any
from django.db.models import Q
from django.conf import settings
from catalogue.models import Product, Category
from users.models import User
from .models import ChatSession, ChatMessage, ProductRecommendation, ChatbotConfig
from decouple import config

class ChatbotService:
    def __init__(self):
        self.openai_api_key = config('OPENAI_API_KEY', default='')
        self.client = None
        if self.openai_api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.openai_api_key)
            except Exception as e:
                print(f"Error initializing OpenAI client: {e}")
                self.client = None
    
    def get_or_create_session(self, session_id: str = None, user_id: int = None) -> ChatSession:
        """Get existing session or create new one"""
        if session_id:
            session, created = ChatSession.objects.get_or_create(
                session_id=session_id,
                defaults={'user_id': user_id}
            )
        else:
            session_id = str(uuid.uuid4())
            session = ChatSession.objects.create(
                session_id=session_id,
                user_id=user_id
            )
        return session
    
    def get_products_data(self) -> List[Dict[str, Any]]:
        """Get all products data for context"""
        products = Product.objects.filter(is_active=True).select_related('category')
        products_data = []
        
        for product in products:
            product_data = {
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': float(product.current_price()),
                'category': product.category.name if product.category else 'Uncategorized',
                'is_flash_sale': product.is_flash_sale_active(),
                'flash_sale_price': float(product.flash_sale_price) if product.flash_sale_price else None,
            }
            products_data.append(product_data)
        
        return products_data
    
    def get_categories_data(self) -> List[Dict[str, Any]]:
        """Get all categories data for context"""
        categories = Category.objects.filter(is_active=True)
        return [{'id': cat.id, 'name': cat.name, 'description': cat.description} for cat in categories]
    
    def create_system_prompt(self) -> str:
        """Create system prompt with product information"""
        products_data = self.get_products_data()
        categories_data = self.get_categories_data()
        
        system_prompt = f"""
Bạn là một chatbot thông minh cho trang web EatsNDrinks - một trang web bán đồ ăn và thức uống. Nhiệm vụ của bạn là:

1. Trả lời các câu hỏi về sản phẩm
2. Đề xuất sản phẩm phù hợp dựa trên yêu cầu của khách hàng
3. Cung cấp thông tin về giá cả, khuyến mãi
4. Hỗ trợ tìm kiếm sản phẩm theo danh mục

Dữ liệu sản phẩm hiện có:
- Tổng cộng {len(products_data)} sản phẩm
- {len(categories_data)} danh mục

Danh mục sản phẩm:
{json.dumps(categories_data, ensure_ascii=False, indent=2)}

Sản phẩm:
{json.dumps(products_data, ensure_ascii=False, indent=2)}

Hướng dẫn trả lời:
- Khi khách hàng chào hỏi (xin chào, hello, hi): Chỉ chào lại và giới thiệu về khả năng của bạn, KHÔNG đề xuất sản phẩm
- Khi khách hàng hỏi chung chung: Giới thiệu về trang web và hỏi họ muốn tìm gì
- Khi khách hàng hỏi về sản phẩm cụ thể: Cung cấp thông tin chi tiết
- Khi khách hàng muốn tìm sản phẩm theo danh mục: Đề xuất các sản phẩm phù hợp
- Khi có khuyến mãi (flash_sale): Nhấn mạnh thông tin này
- Trả lời bằng tiếng Việt, thân thiện và hữu ích

QUAN TRỌNG - Đề xuất sản phẩm:
- CHỈ đề xuất sản phẩm khi khách hàng yêu cầu tìm kiếm, đề xuất, hoặc hỏi về sản phẩm cụ thể
- KHÔNG đề xuất sản phẩm khi khách hàng chỉ chào hỏi
- Khi đề xuất, hãy đề xuất 3-5 sản phẩm phù hợp từ danh sách trên
- Nếu được yêu cầu đề xuất sản phẩm, hãy trả về danh sách ID sản phẩm được đề xuất trong format JSON: {{"recommendations": [id1, id2, id3]}}
- Nếu không có format JSON, hãy đề xuất sản phẩm bằng cách nhắc tên sản phẩm trong câu trả lời

Hãy trả lời ngắn gọn, thân thiện và hữu ích!
"""
        return system_prompt
    
    def get_chat_history(self, session: ChatSession, limit: int = 10) -> List[Dict[str, str]]:
        """Get recent chat history for context"""
        messages = ChatMessage.objects.filter(session=session).order_by('-timestamp')[:limit]
        history = []
        for msg in reversed(messages):  # Reverse to get chronological order
            role = "user" if msg.message_type == "user" else "assistant"
            history.append({"role": role, "content": msg.content})
        return history
    
    def analyze_user_intent(self, message: str) -> Dict[str, Any]:
        """Analyze user intent and extract relevant information"""
        intent_analysis = {
            'intent': 'general_query',
            'category_filter': None,
            'price_range': None,
            'keywords': [],
            'is_search': False,
            'is_recommendation_request': False,
            'is_greeting': False,
            'is_general_question': False,
            'is_flash_sale': False
        }
        
        message_lower = message.lower()
        
        # Check for greeting intent
        greeting_keywords = ['xin chào', 'chào', 'hello', 'hi', 'hey', 'chào bạn', 'xin chào bạn']
        if any(keyword in message_lower for keyword in greeting_keywords):
            intent_analysis['is_greeting'] = True
            intent_analysis['intent'] = 'greeting'
        
        # Check for general questions
        question_keywords = ['là gì', 'gì vậy', 'thế nào', 'có gì', 'bán gì', 'có những gì']
        if any(keyword in message_lower for keyword in question_keywords):
            intent_analysis['is_general_question'] = True
            intent_analysis['intent'] = 'general_question'
        
        # Check for search intent
        search_keywords = ['tìm', 'kiếm', 'có', 'bán', 'mua']
        if any(keyword in message_lower for keyword in search_keywords):
            intent_analysis['is_search'] = True
            intent_analysis['intent'] = 'search'
        
        # Check for recommendation intent
        rec_keywords = ['đề xuất', 'gợi ý', 'nên', 'phù hợp', 'ngon', 'tốt', 'hay']
        if any(keyword in message_lower for keyword in rec_keywords):
            intent_analysis['is_recommendation_request'] = True
            intent_analysis['intent'] = 'recommendation'
        
        # Check for flash sale intent
        flash_sale_keywords = ['flash sale', 'khuyến mãi', 'giảm giá', 'sale', 'đang khuyến mãi']
        if any(keyword in message_lower for keyword in flash_sale_keywords):
            intent_analysis['intent'] = 'flash_sale'
            intent_analysis['is_flash_sale'] = True
        
        # Extract category keywords
        categories = Category.objects.filter(is_active=True)
        for category in categories:
            if category.name.lower() in message_lower:
                intent_analysis['category_filter'] = category.id
                intent_analysis['intent'] = 'category_search'
                break
        
        # Extract price keywords
        price_keywords = ['rẻ', 'giá thấp', 'dưới', 'trên', 'đắt', 'cao cấp']
        for keyword in price_keywords:
            if keyword in message_lower:
                intent_analysis['keywords'].append(keyword)
                if intent_analysis['intent'] == 'general_query':
                    intent_analysis['intent'] = 'price_search'
        
        print('[DEBUG] intent_analysis:', intent_analysis)
        return intent_analysis
    
    def get_recommendations(self, intent_analysis: Dict[str, Any], limit: int = 5) -> List[Product]:
        """Get product recommendations based on intent analysis"""
        products = Product.objects.filter(is_active=True)
        
        # Nếu intent là flash_sale thì chỉ lấy sản phẩm đang flash sale
        if intent_analysis.get('is_flash_sale'):
            products = [p for p in products if p.is_flash_sale_active()]
            products = sorted(products, key=lambda p: p.flash_sale_price or p.price)[:limit]
            return products
        
        # Apply category filter
        if intent_analysis['category_filter']:
            products = products.filter(category_id=intent_analysis['category_filter'])
        
        # Apply price filters
        if 'rẻ' in intent_analysis['keywords'] or 'giá thấp' in intent_analysis['keywords']:
            products = products.order_by('price')[:limit]
        elif 'đắt' in intent_analysis['keywords'] or 'cao cấp' in intent_analysis['keywords']:
            products = products.order_by('-price')[:limit]
        else:
            # Default: recommend products with flash sale first, then by popularity
            products = products.order_by('-flash_sale_price', '-created_at')[:limit]
        
        print('[DEBUG] Số sản phẩm flash sale recommendations:', len(products), [p.id for p in products])
        return list(products)
    
    def convert_product_to_dict(self, product: Product) -> Dict[str, Any]:
        """Convert Product object to dictionary for JSON serialization"""
        return {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': float(product.current_price()),
            'category': product.category.name if product.category else 'Uncategorized',
            'is_flash_sale': product.is_flash_sale_active(),
            'flash_sale_price': float(product.flash_sale_price) if product.flash_sale_price else None,
            'mainimage': product.mainimage.url if product.mainimage else None,
        }
    
    def generate_response(self, message: str, session: ChatSession) -> Dict[str, Any]:
        """Generate chatbot response using OpenAI"""
        if not self.openai_api_key or not self.client:
            return self.generate_fallback_response(message, session)
        try:
            system_prompt = self.create_system_prompt()
            chat_history = self.get_chat_history(session)
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(chat_history)
            messages.append({"role": "user", "content": message})
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            bot_response = response.choices[0].message.content
            # Try to extract recommendations from response
            recommendations = []
            intent_analysis = self.analyze_user_intent(message)
            try:
                # Method 1: Look for JSON format
                if '{"recommendations":' in bot_response:
                    import re
                    json_match = re.search(r'\{.*\}', bot_response)
                    if json_match:
                        rec_data = json.loads(json_match.group())
                        if 'recommendations' in rec_data:
                            product_ids = rec_data['recommendations']
                            recommended_products = Product.objects.filter(
                                id__in=product_ids, is_active=True
                            )
                            recommendations = [self.convert_product_to_dict(p) for p in recommended_products]
                # Method 2: Extract product names from text and find matching products
                if not recommendations:
                    # Get all product names for matching
                    all_products = Product.objects.filter(is_active=True)
                    # Nếu intent là flash sale, chỉ lấy sản phẩm đang flash sale
                    if intent_analysis.get('is_flash_sale'):
                        all_products = [p for p in all_products if p.is_flash_sale_active()]
                    product_names = {p.name.lower(): p for p in all_products}
                    response_lower = bot_response.lower()
                    found_products = []
                    for product_name, product in product_names.items():
                        if product_name in response_lower:
                            found_products.append(product)
                    # Take first 5 products found
                    recommendations = [self.convert_product_to_dict(p) for p in found_products[:5]]
                # Method 3: Only use intent analysis if it's NOT a greeting
                if not recommendations:
                    # Only recommend if it's not a greeting
                    if not intent_analysis['is_greeting']:
                        recommended_products = self.get_recommendations(intent_analysis, 5)
                        recommendations = [self.convert_product_to_dict(p) for p in recommended_products]
            except Exception as e:
                print(f"Error extracting recommendations: {e}")
                # Fallback to intent analysis only if not greeting
                if not intent_analysis['is_greeting']:
                    recommended_products = self.get_recommendations(intent_analysis, 5)
                    recommendations = [self.convert_product_to_dict(p) for p in recommended_products]

            # --- CUSTOM FLASH SALE MESSAGE ---
            if intent_analysis.get('is_flash_sale'):
                if recommendations:
                    msg = "Hiện tại, có một số sản phẩm đang được giảm giá flash sale, bao gồm:\n\n"
                    for idx, p in enumerate(recommendations, 1):
                        msg += f"{idx}. {p['name']} - Giá flash sale: {int(p['flash_sale_price']):,} VND\n"
                    msg += "\nNếu bạn quan tâm đến bất kỳ sản phẩm nào, hãy cho mình biết để được hỗ trợ thêm nhé!"
                else:
                    msg = "Hiện tại không có sản phẩm nào đang flash sale."
            else:
                msg = bot_response
            print('[DEBUG] Số sản phẩm flash sale recommendations:', len(recommendations), [p['id'] for p in recommendations])
            return {
                'response': msg,
                'recommendations': recommendations,
                'metadata': {
                    'model_used': 'gpt-3.5-turbo',
                    'tokens_used': response.usage.total_tokens if hasattr(response, 'usage') else 0
                }
            }
        except Exception as e:
            # Log the error for debugging
            print(f"OpenAI API Error: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            # Return fallback with error info
            fallback_result = self.generate_fallback_response(message, session)
            fallback_result['metadata']['error'] = str(e)
            fallback_result['metadata']['error_type'] = type(e).__name__
            return fallback_result
    
    def generate_fallback_response(self, message: str, session: ChatSession) -> Dict[str, Any]:
        """Generate fallback response when OpenAI is not available"""
        intent_analysis = self.analyze_user_intent(message)
        recommendations = []
        
        # Xử lý các intent khác nhau
        if intent_analysis['is_greeting']:
            response = "Xin chào! Tôi là chatbot của EatsNDrinks. Tôi có thể giúp bạn tìm kiếm và đề xuất sản phẩm. Bạn muốn tìm gì?"
        
        elif intent_analysis['is_general_question']:
            response = "EatsNDrinks là trang web bán đồ ăn và thức uống. Chúng tôi có nhiều loại sản phẩm như đồ uống, thức ăn nhanh, và các món ăn khác. Bạn muốn tìm hiểu về sản phẩm nào?"
        
        elif intent_analysis['is_search'] or intent_analysis['is_recommendation_request']:
            recommendations = self.get_recommendations(intent_analysis)
            if recommendations:
                product_names = [p.name for p in recommendations[:3]]
                response = f"Tôi đề xuất cho bạn: {', '.join(product_names)}. Bạn có muốn biết thêm thông tin về sản phẩm nào không?"
            else:
                response = "Xin lỗi, tôi không tìm thấy sản phẩm phù hợp. Bạn có thể thử tìm kiếm với từ khóa khác."
        
        elif intent_analysis['intent'] == 'category_search':
            recommendations = self.get_recommendations(intent_analysis)
            if recommendations:
                category_name = recommendations[0].category.name if recommendations[0].category else "danh mục này"
                product_names = [p.name for p in recommendations[:3]]
                response = f"Trong {category_name}, tôi có: {', '.join(product_names)}. Bạn muốn biết thêm về sản phẩm nào?"
            else:
                response = "Xin lỗi, hiện tại không có sản phẩm trong danh mục này."
        
        elif intent_analysis['intent'] == 'price_search':
            recommendations = self.get_recommendations(intent_analysis)
            if recommendations:
                if 'rẻ' in intent_analysis['keywords'] or 'giá thấp' in intent_analysis['keywords']:
                    response = f"Sản phẩm có giá tốt: {', '.join([p.name for p in recommendations[:3]])}. Bạn có muốn xem thêm không?"
                else:
                    response = f"Sản phẩm cao cấp: {', '.join([p.name for p in recommendations[:3]])}. Bạn có muốn xem thêm không?"
            else:
                response = "Xin lỗi, không tìm thấy sản phẩm phù hợp với yêu cầu giá của bạn."
        
        else:
            # Default response for unclear intent
            response = "Xin chào! Tôi có thể giúp bạn tìm kiếm sản phẩm. Bạn có thể hỏi tôi về đồ uống, thức ăn, hoặc yêu cầu đề xuất sản phẩm."
        
        return {
            'response': response,
            'recommendations': [self.convert_product_to_dict(p) for p in recommendations],
            'metadata': {
                'model_used': 'fallback',
                'intent_analysis': intent_analysis
            }
        }
    
    def process_chat(self, message: str, session_id: str = None, user_id: int = None) -> Dict[str, Any]:
        """Main method to process chat message"""
        # Get or create session
        session = self.get_or_create_session(session_id, user_id)
        
        # Save user message
        user_message = ChatMessage.objects.create(
            session=session,
            message_type='user',
            content=message
        )
        
        # Generate response
        response_data = self.generate_response(message, session)
        
        # Save bot response
        bot_message = ChatMessage.objects.create(
            session=session,
            message_type='bot',
            content=response_data['response'],
            metadata=response_data['metadata']
        )
        
        # Save recommendations
        for product_dict in response_data['recommendations']:
            try:
                product = Product.objects.get(id=product_dict['id'])
                ProductRecommendation.objects.create(
                    message=bot_message,
                    product=product,
                    confidence_score=0.8,  # Default confidence
                    reason="Được đề xuất bởi chatbot"
                )
            except Product.DoesNotExist:
                pass
        
        return {
            'message': response_data['response'],
            'session_id': session.session_id,
            'recommendations': response_data['recommendations'],
            'metadata': response_data['metadata']
        } 