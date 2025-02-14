import os
import sys

current_file_path = os.path.abspath(__file__)
parent_directory = os.path.dirname(current_file_path)
root_directory = os.path.dirname(parent_directory)
sys.path.append(root_directory)


import jdatetime
from flask import Flask, jsonify, render_template, request
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils import preprocess_text_fa

app = Flask(__name__)

# Connect to mongodb
client = MongoClient("mongodb://127.0.0.1:27017")
db = client["news_scraper_data"]
news = db["news"]


def to_persian_date(dt):
    jalali_date = jdatetime.datetime.fromgregorian(datetime=dt)
    persian_months = [
        "فروردین",
        "اردیبهشت",
        "خرداد",
        "تیر",
        "مرداد",
        "شهریور",
        "مهر",
        "آبان",
        "آذر",
        "دی",
        "بهمن",
        "اسفند",
    ]
    return f"{jalali_date.day} {persian_months[jalali_date.month - 1]} {jalali_date.year} - {jalali_date.hour}:{'0' if jalali_date.minute < 10 else ''}{jalali_date.minute}:{'0' if jalali_date.second < 10 else ''}{jalali_date.second}"


def search(query, offset=10):
    processed_query = preprocess_text_fa(query)
    query_terms = processed_query.split()

    # جستجوی اولیه در MongoDB با منطق OR برای هر کلمه
    mongo_clauses = []
    for term in query_terms:
        mongo_clauses.append({"processed_title": {"$regex": term, "$options": "i"}})
        mongo_clauses.append(
            {"processed_content_text": {"$regex": term, "$options": "i"}}
        )

    search_query = {"$or": mongo_clauses}

    # دریافت مستندات مرتبط و ذخیره در لیست
    relevant_docs = list(news.find(search_query).limit(100))
    if not relevant_docs:
        return None

    # استخراج متن پردازش شده مستندات
    documents = [doc["processed_content_text"] for doc in relevant_docs]

    # آموزش TF-IDF روی مستندات + کوئری
    vectorizer = TfidfVectorizer()
    all_texts = documents + [processed_query]
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    # جدا کردن بردارهای مستندات و کوئری
    doc_vectors = tfidf_matrix[:-1]
    query_vector = tfidf_matrix[-1]

    # محاسبه شباهت کسینوسی
    similarities = cosine_similarity(query_vector, doc_vectors)

    # مرتبسازی بر اساس شباهت
    sorted_indices = similarities.argsort()[0][::-1]
    top_results = [relevant_docs[idx] for idx in sorted_indices[:offset]]

    return (top_results, processed_query)


@app.route("/", methods=["GET"])
def handle_home():
    return render_template("home.html")


@app.route("/search", methods=["POST"])
def handle_search():
    query = request.form["query"]
    if not query:
        return jsonify({"error": "Please provide query"}), 400

    results, processed_query = search(query, 10)
    if results == None:
        return render_template("home.html")

    for result in results:
        result["_id"] = str(result["_id"])
        result["updatedAt"] = to_persian_date(result["updatedAt"])

    return render_template(
        "result.html", results=results, query=query, processed_query=processed_query
    )


if __name__ == "__main__":
    app.run(debug=True)
