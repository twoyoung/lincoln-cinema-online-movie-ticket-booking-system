# lincoln-cinema-online-movie-ticket-booking-system

- File structure
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

- steps to run this application
  - Install the packages from requirements.txt
  ```
  pip install -r requirements.txt
  ```
  - Setup database using the script create_db.py
    ```
    ./.venv/bin/python create_db.py
    ```
    cinema.db will be generated under folder instance
  - If you want to visualize the data from SQLiteStudio, import the cinema.db to  SQLiteStudio
  - Populate database from db_data.json
    ```
    ./.venv/bin/python populateDatabaseFromJsonFileScript.py
    ```
  - Now run the application locally
    ```
    flask run
    ```
       
  
