py -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

streamlit run app.py

cd backend
cd logic_service
uvicorn main:app --host 0.0.0.0 --port 8001

cd backend
cd database_service
uvicorn main:app --host 0.0.0.0 --port 8000