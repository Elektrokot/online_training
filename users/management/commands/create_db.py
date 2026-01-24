import psycopg
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Creates the database specified in DATABASES if it does not exist"

    def handle(self, *args, **options):
        db_settings = settings.DATABASES["default"]
        db_name = db_settings["NAME"]
        db_user = db_settings["USER"]
        db_password = db_settings["PASSWORD"]
        db_host = db_settings["HOST"]
        db_port = db_settings["PORT"]

        # Подключаемся к PostgreSQL (нужно подключиться к служебной базе, например, postgres)
        conn = psycopg.connect(
            dbname="postgres",  # Подключаемся к служебной базе
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
        )
        conn.autocommit = True  # Нужно для выполнения CREATE DATABASE
        cursor = conn.cursor()

        # Проверяем, существует ли база данных
        cursor.execute(
            "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_name,)
        )
        exists = cursor.fetchone()

        if not exists:
            try:
                cursor.execute(f"CREATE DATABASE {db_name};")
                self.stdout.write(
                    self.style.SUCCESS(f'Database "{db_name}" created successfully.')
                )
            except psycopg.Error as e:
                self.stdout.write(self.style.ERROR(f"Error creating database: {e}"))
        else:
            self.stdout.write(
                self.style.WARNING(f'Database "{db_name}" already exists.')
            )

        cursor.close()
        conn.close()
