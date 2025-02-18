# Food Website

This is a simple Flask website that displays food recipes. It fetches data from [TheMealDB API](https://themealdb.com), and you can see a live static design of the website [here](https://default3.pythonanywhere.com/).

## Installation

To run this project locally, follow these steps:

1. Install the required dependencies using pip:
```
pip install -r requirements.txt
```
2. Before starting the website, delete the old `testdb.db` file.

3. New Database will automatically be created after executing the following command:
```
python main.py
```

This command should create a fresh new database. 
If the database is not created, execute `database.py` to create the database with the necessary tables.

Usage
You can access the website by opening your web browser and navigating to the address where the website is hosted or on 127.0.0.1 .

Contributing
If you'd like to contribute to this project, please open an issue or submit a pull request. We welcome your contributions and ideas!

License
This project is open-source and available under the MIT License.
