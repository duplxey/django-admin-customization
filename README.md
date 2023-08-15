# Django Admin Site Customization

## Want to learn how to build this?

Check out the [post](#).

## Want to use this project?

1. Fork/Clone

1. Create and activate a virtual environment:

    ```sh
    $ python3.11 -m venv venv && source venv/bin/activate
    ```

1. Install the requirements:

    ```sh
    (venv)$ pip install -r requirements.txt
    ```

1. Apply the migrations:

    ```sh
    (venv)$ python manage.py migrate
    ```

1. Create a superuser and populate the database:

    ```sh
    (venv)$ python manage.py createsuperuser
    (venv)$ python manage.py populate_db
    ```
	
1. Run the development server:

    ```sh
    (venv)$ python manage.py runserver
    ```
    
1. Your Django admin site should be accessible at [http://localhost:8000/secretadmin/](http://localhost:8000/secretadmin/).