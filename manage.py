#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    if int(os.environ.get("WAGTAIL_PRODUCTION", 0)):
        os.environ.setdefault(
            "DJANGO_SETTINGS_MODULE", "lccwebsite.settings.production"
        )
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lccwebsite.settings.dev")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
