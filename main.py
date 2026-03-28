from fastapi import FastAPI


app = FastAPI()


app.get("/")


def home():
    return "Hello to my project"
