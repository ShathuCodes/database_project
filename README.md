# Forensic Medical Department MIS

A complete database system and web dashboard for a forensic medical department. 

## 1. Prerequisites
- Python 3.10+
- PostgreSQL server installed and running

## 2. Database Setup
1. Open pgAdmin or your PostgreSQL command line.
2. Create a new database named `forensic_db`.
3. Create a file named `.env` in the root folder of this project (next to `run.py`).
4. Add your PostgreSQL credentials to the `.env` file like this:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=forensic_db
DB_USER=postgres
DB_PASSWORD=your_actual_postgres_password
SECRET_KEY=your_secret_key_here
```

## 3. Installation
1. Open a terminal in the project folder.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - **Windows:** `venv\Scripts\activate`
   - **Mac/Linux:** `source venv/bin/activate`
4. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 4. Initialization
Once your database is created and your `.env` file is set up, initialize the database schema and default admin account by running:

```bash
flask --app run.py init-db
```
*(This will automatically create tables and the default `admin` / `Password123` account)*

## 5. Running the Application
Start the development server:

```bash
python run.py
```

Now, open your web browser and navigate to `http://localhost:5000`.
