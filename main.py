from fastapi import FastAPI, UploadFile, File, Header
from db import users
from auth import *
from models import *
import cv2
import numpy as np
import os
import json

app = FastAPI()


# ================= AUTH =================

@app.post("/signup")
def signup(data:dict):

    if users.find_one({"email":data["email"]}):
        return "User exists"

    hashed=hash_pw(data["password"])

    user=new_user(data["email"],hashed,data.get("ref"))

    users.insert_one(user)

    # Referral rewards
    if data.get("ref"):
        users.update_one({"email":data["ref"]},{"$inc":{"coins":10}})
        users.update_one({"email":data["email"]},{"$inc":{"coins":20}})

    return "Signup success"


@app.post("/login")
def login(data:dict):

    u=users.find_one({"email":data["email"]})
    if not u:
        return {"error":"no user"}

    if not verify_pw(data["password"],u["password"]):
        return {"error":"bad pass"}

    token=create_token(data["email"])
    return {"token":token}


# ================= COINS =================

@app.get("/coins")
def coins(Authorization: str = Header()):

    email=get_email(Authorization)
    u=users.find_one({"email":email})
    return {"coins":u["coins"]}


# ================= VIDEO ANALYSIS =================

@app.post("/analyze")
async def analyze(video: UploadFile = File(...), Authorization: str = Header()):

    email=get_email(Authorization)
    u=users.find_one({"email":email})

    if u["coins"] < 5:
        return {"error":"not enough coins"}

    users.update_one({"email":email},{"$inc":{"coins":-5}})

    # Simple mock scoring logic
    score=np.random.randint(50,100)
    return {
        "score":int(score),
        "engagement":int(score*0.8),
        "viral":int(score*0.6)
    }


# ================= THUMB AI =================

@app.post("/thumbnail-score")
async def thumb(image: UploadFile = File(...), Authorization: str = Header()):

    get_email(Authorization)

    contents=await image.read()
    arr=np.frombuffer(contents,np.uint8)
    img=cv2.imdecode(arr,cv2.IMREAD_COLOR)
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    brightness=np.mean(gray)
    contrast=gray.std()
    sharp=cv2.Laplacian(gray,cv2.CV_64F).var()

    score=int((brightness/255*30)+(contrast/128*30)+(sharp/500*40))
    score=max(0,min(score,100))

    return {
        "score":score,
        "brightness":float(brightness),
        "contrast":float(contrast),
        "sharpness":float(sharp)
    }


# ================= KO-FI =================

@app.post("/kofi-webhook")
async def kofi(payload:dict):

    if payload.get("verification_token") != os.getenv("KOFI_SECRET"):
        return {"status":"bad token"}

    email=payload.get("email")

    users.update_one({"email":email},{"$inc":{"coins":1000}})

    return {"status":"coins added"}