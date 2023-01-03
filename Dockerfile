FROM python:3.9-alpine
EXPOSE 5000/tcp
WORKDIR /app
COPY /src /app/    
RUN pip install flask flask_cors bs4 requests lxml redis redis[hiredis]
CMD ["flask", "run", "--host", "0.0.0.0"]