

Before any database operation like `<Model>.objects.all()` you have to migrate your current model with

```
python manage.py makemigrations
python manage.py migrate
```
