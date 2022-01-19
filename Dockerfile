FROM python:3.6.5-slim-stretch
ADD . /dataApplication1
WORKDIR /dataApplication1
RUN pip install -r req.txt
CMD ["python3" , "dataAPI.py" ]

