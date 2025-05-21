import io
import os
import django

# 👇 Thiết lập đúng module cấu hình settings.py
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eatsndrinks.settings")

# 👇 Khởi tạo Django
django.setup()

# 👇 Dump dữ liệu ra file UTF-8
with io.open("data.json", "w", encoding="utf-8") as f:
    from django.core.management import call_command
    call_command('dumpdata', indent=2, stdout=f)
