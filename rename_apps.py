from django.db import connection

def my_custom_sql():
    with connection.cursor() as cursor:
        cursor.execute("UPDATE django_content_type SET app_label='clientaccounts' WHERE app_label='userprofile'")

if __name__== "__main__":
    my_custom_sql()
