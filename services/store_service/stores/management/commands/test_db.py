
from django.core.management import BaseCommand

from django.db import connection


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        cursor = connection.cursor()
        cursor.execute("SELECT 1;")
        print(cursor.fetchone())
