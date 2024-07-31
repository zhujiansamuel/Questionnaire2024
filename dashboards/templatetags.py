# import base64
# import json
# import os
# import platform
# import sys
# import time
#
# from simpleui.templatetags.simpletags import get_current_app
#
# import django
# from django import template
# from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
# from django.core.serializers.json import DjangoJSONEncoder
# from django.db import models
# from django.urls import is_valid_path, reverse
#
# try:
#     from django.utils.encoding import force_text
# except:
#     from django.utils.encoding import force_str as force_text
# from django.utils.functional import Promise
# from django.utils.html import format_html
# from django.utils.safestring import mark_safe
#
# register = template.Library()
#
# PY_VER = sys.version[0]  # 2 or 3
# from django.utils.translation import gettext_lazy as _
#
#
# from django.utils.translation import gettext_lazy as _
#
#
# @register.simple_tag(takes_context=True)
# def get_summery_url(context):
#     pass
#