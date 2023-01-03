FROM python:3.9
EXPOSE 5000/tcp
WORKDIR /app
COPY /src /app/    
# RUN apk update && apk add python3-dev \
#     gcc \
#     libc-dev \
#     libffi-dev
RUN pip install flask flask_cors bs4 requests lxml redis redis[hiredis] psutil
CMD ["flask", "run", "--host", "0.0.0.0"]