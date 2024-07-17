FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

WORKDIR /app/
COPY app/src/requirements.txt /app/src/requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r ./src/requirements.txt
RUN pip3 install uvicorn[standard]
RUN pip3 install websockets

COPY ./app /app
ENV PYTHONPATH=/app


#CMD python src/initial_data.py && uvicorn --workers=1 --forwarded-allow-ips '*' --host 0.0.0.0 --port 80 src.main:app --reload

CMD alembic upgrade head && python src/initial_data.py && uvicorn --workers=1 --forwarded-allow-ips '*' --host 0.0.0.0 --port 80 src.main:app --reload
#CMD alembic revision --autogenerate -m "Payment Table Added" && python src/initial_data.py && uvicorn --workers=1 --forwarded-allow-ips '*' --host 0.0.0.0 --port 80 src.main:app --reload


