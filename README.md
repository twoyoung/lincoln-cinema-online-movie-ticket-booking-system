# lincoln-cinema-online-movie-ticket-booking-system

- This is a simple web application designed for managing a cinema ticket booking system.   
- It is built using Object-Oriented Programming (OOP) principles and follows the Model-View-Controller (MVC) architecture.   
- To adhere to the concept of a fat model and thin controller, most of the business logic, data validation, and all database interactions are encapsulated within the model methods. Controller's primary role is to handle incoming requests, delegate processing to the models, and then pass the results to the views.
- The application utilizes SQLAlchemy for its database management. Before running the code, please set up and populate the database following the instructions below.

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
    
       
  
