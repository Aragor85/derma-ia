import joblib

content_df = joblib.load("models/content.pkl")
surprise_df = joblib.load("models/surprise.pkl")

print(content_df.head())
print(surprise_df.head())
