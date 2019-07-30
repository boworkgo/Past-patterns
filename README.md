# Past Patterns

This site lets someone write about their day and analyzes what they do, hopefully revealing some past patterns.

## Installation

Use pip to install Django.

```bash
pip install django --user
```

## Usage

Clone this repository and navigate to it. Create `past/secret.py` and put in it `SECRET_KEY=[your secret key]`. Then, type

```bash
python manage.py migrate
python manage.py makemigrations
python manage.py runserver
```

and navigate to `localhost:8000/posts/`.

## Sources

- [Django official tutorial](https://docs.djangoproject.com/en/2.2/intro/tutorial01/)
- [Bootstrap examples](https://getbootstrap.com/docs/4.3/examples/)
- [How to make a readme](https://www.makeareadme.com/)
- [Pandas official tutorial](https://pandas.pydata.org/pandas-docs/stable/getting_started/10min.html)
