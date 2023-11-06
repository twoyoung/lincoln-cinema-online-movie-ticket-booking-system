# lincoln-cinema-online-movie-ticket-booking-system

- Deployed on pythonAnywhere: http://tooyoung.pythonanywhere.com/
- Front-end: HTML, JS, Tailwind CSS; Back-end: Python + Flask; Database: SQLAlchemy + SQLite
- This is a simple web application designed for managing a cinema ticket booking system.
- It is built using Object-Oriented Programming (OOP) principles and follows the Model-View-Controller (MVC) architecture.
- To adhere to the concept of a fat model and thin controller, most of the business logic, data validation, and all database interactions are encapsulated within the model methods. The primary role of controller is to handle incoming requests, delegate processing to the models, and then pass the results to the views.
- The application employs SQLAlchemy for database management considering that it offers an ORM (Object-Relational Mapping) approach. This facilitates intuitive handling of database interactions through object manipulation, which is in line with Object-Oriented Programming (OOP) principles. Prior to executing the code, please follow the instructions provided below to set up and populate the database.

## File structure

```
lincoln-cinema-online-movie-ticket-booking-system/
├── .venv
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── movieModel.py
│   │   ├── paymentModel.py
│   │   └── userModel.py
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── authController.py
│   │   └── movieController.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── templates/
│   └── static/
├── run.py
├── test/
│   ├── test_login.py
│   └── conftest.py
├── create_db.py  # script to create sqlAlchemy database
├── db_data.json   # json data to populate the database
├── generateSeats.py  # script to generate seats data
├── populateDatabaseFromJsonFileScript.py  # script to populate data in db_data.json into created database
├── instance/
│   └── cinema.db  # database created by create_db.py
└── requirements.txt
```

## Steps to set up and populate sqlAlchemy database before running the application
  1. Install the packages from requirements.txt
     ```
     pip install -r requirements.txt
     ```
    
  2. Setup database using the script create_db.py.
     
     ```
     ./.venv/bin/python create_db.py
     ```
     After running the script, cinema.db will be generated under folder instance.   
     If you want to visualize the data from SQLiteStudio, import the cinema.db to  SQLiteStudio.
     
  4. Populate database from db_data.json
     ```
     ./.venv/bin/python populateDatabaseFromJsonFileScript.py
     ```
  5. Now run the application locally
     ```
     flask run
     ```
## Default account
- customer:
  - username: customer
  - password: Password
- staff:
  - username: staff
  - password: Password
- admin:
  - username: admin
  - password: Password
