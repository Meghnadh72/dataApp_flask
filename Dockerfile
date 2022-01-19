FROM python:3.6.5-slim-stretch
ADD . /dataApplication1
WORKDIR /dataApplication1
RUN pip install -r req.txt
RUN ["export", "FLASK_ENV=development"]
RUN ["export", "FLASK_APP=dataAPI"]
CMD ["tail" , "-f", "dev/null" ]
