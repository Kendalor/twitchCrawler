FROM python
COPY . /app
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install --no-use-wheel --allow-all-external -r requirements.txt
EXPOSE 5000
CMD python run.py