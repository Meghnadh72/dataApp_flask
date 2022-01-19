FROM python:3.6.5-slim-stretch
ADD . /dataApplication2
WORKDIR /dataApplication2
RUN pip install -r req.txt
RUN ["export", "FLASK_ENV=development"]
RUN ["export", "FLASK_APP=dataAPI"]
CMD ["flask" , "run" ]
