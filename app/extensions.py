from pymongo import MongoClient

# MongoDB Atlas connection
client = MongoClient(
    "mongodb+srv://sk_2014:1793@cluster0.qsaud7u.mongodb.net/github_events?retryWrites=true&w=majority"
)

db = client["github_events"]
collection = db["events"]
