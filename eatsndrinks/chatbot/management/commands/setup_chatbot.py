from django.core.management.base import BaseCommand
from chatbot.models import ChatbotConfig
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Setup default chatbot configuration'

    def handle(self, *args, **options):
        self.stdout.write('Setting up chatbot configuration...')
        
        # Create default config if it doesn't exist
        config, created = ChatbotConfig.objects.get_or_create(
            name='Default Config',
            defaults={
                'model_name': 'gpt-3.5-turbo',
                'max_tokens': 1000,
                'temperature': 0.7,
                'system_prompt': 'Bạn là chatbot thông minh cho trang web EatsNDrinks.',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('✅ Created default chatbot configuration')
            )
        else:
            self.stdout.write(
                self.style.WARNING('⚠️  Default configuration already exists')
            )
        
        # Check OpenAI API key
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            self.stdout.write(
                self.style.SUCCESS('✅ OpenAI API key found')
            )
        else:
            self.stdout.write(
                self.style.WARNING('⚠️  OpenAI API key not found. Chatbot will use fallback mode.')
            )
            self.stdout.write(
                '   Add OPENAI_API_KEY to your .env file to enable AI features.'
            )
        
        self.stdout.write(
            self.style.SUCCESS('🎉 Chatbot setup completed!')
        )
        self.stdout.write('')
        self.stdout.write('Next steps:')
        self.stdout.write('1. Run: python manage.py migrate')
        self.stdout.write('2. Run: python manage.py runserver')
        self.stdout.write('3. Test: python chatbot_demo.py') 