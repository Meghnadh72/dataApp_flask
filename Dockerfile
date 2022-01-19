FROM python:3.6.5-slim-stretch
ADD . /dataApplication2
WORKDIR /dataApplication2
RUN pip install -r req.txt
CMD ["python" , "app/dataAPI.py" ]

