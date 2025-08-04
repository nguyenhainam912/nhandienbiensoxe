py -m venv venv

venv\Scripts\activate

pip install -r requirements.txt


cd nhandienbiensoxe
streamlit run app.py

cd nhandienbiensoxe
cd backend
cd logic_service
uvicorn main:app --host 0.0.0.0 --port 8001


cd nhandienbiensoxe
cd backend
cd database_service
uvicorn main:app --host 0.0.0.0 --port 8000