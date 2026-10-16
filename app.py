from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import plotly.express as px
import plotly.utils
import json
import os
from io import BytesIO

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_FILE = os.path.join(DATA_DIR, "marketing_data.csv")
os.makedirs(DATA_DIR, exist_ok=True)

REQUIRED_COLUMNS = [
    "date", "visitors", "page_views", "platform", "likes",
    "comments", "shares", "campaign", "clicks", "conversions", "spend"
]

def create_sample_data():
    rows = [
        ["2026-10-01", 120, 260, "Instagram", 42, 8, 5, "Autumn Sale", 36, 5, 20.0],
        ["2026-10-02", 145, 310, "Facebook", 35, 6, 4, "Autumn Sale", 41, 6, 22.0],
        ["2026-10-03", 180, 390, "LinkedIn", 28, 9, 7, "Brand Awareness", 52, 8, 18.0],
        ["2026-10-04", 160, 340, "Instagram", 56, 12, 9, "Autumn Sale", 48, 7, 25.0],
        ["2026-10-05", 210, 440, "Facebook", 49, 10, 6, "Brand Awareness", 61, 9, 28.0],
        ["2026-10-06", 195, 410, "Instagram", 63, 14, 11, "Product Launch", 58, 10, 30.0],
        ["2026-10-07", 240, 520, "LinkedIn", 37, 11, 8, "Product Launch", 74, 12, 32.0],
        ["2026-10-08", 225, 480, "Facebook", 52, 13, 7, "Autumn Sale", 69, 11, 29.0],
        ["2026-10-09", 270, 570, "Instagram", 72, 16, 13, "Product Launch", 82, 14, 35.0],
        ["2026-10-10", 290, 610, "LinkedIn", 45, 15, 10, "Brand Awareness", 91, 16, 38.0],
    ]
    df = pd.DataFrame(rows, columns=REQUIRED_COLUMNS)
    df.to_csv(DATA_FILE, index=False)

def load_data():
    if not os.path.exists(DATA_FILE):
        create_sample_data()
    df = pd.read_csv(DATA_FILE)
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = "" if col in ["date", "platform", "campaign"] else 0
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    numeric = ["visitors", "page_views", "likes", "comments", "shares", "clicks", "conversions", "spend"]
    for col in numeric:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    for col in ["platform", "campaign"]:
        df[col] = df[col].fillna("Unknown").astype(str)
    return df

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/dashboard")
def dashboard_data():
    df = load_data()
    valid_dates = df.dropna(subset=["date"]).copy()
    total_visitors = int(df["visitors"].sum())
    total_views = int(df["page_views"].sum())
    total_engagements = int((df["likes"] + df["comments"] + df["shares"]).sum())
    total_clicks = int(df["clicks"].sum())
    total_conversions = int(df["conversions"].sum())
    reach_proxy = total_visitors
    engagement_rate = round(total_engagements / reach_proxy * 100, 2) if reach_proxy else 0
    ctr = round(total_clicks / total_views * 100, 2) if total_views else 0

    if not valid_dates.empty:
        traffic = valid_dates.groupby(valid_dates["date"].dt.strftime("%Y-%m-%d"), as_index=False)["visitors"].sum()
        fig_traffic = px.line(traffic, x="date", y="visitors", markers=True, title="Website Visitors Over Time")
    else:
        fig_traffic = px.line(title="Website Visitors Over Time")

    platform = df.groupby("platform", as_index=False)[["likes", "comments", "shares"]].sum()
    platform["engagements"] = platform["likes"] + platform["comments"] + platform["shares"]
    fig_platform = px.bar(platform, x="platform", y="engagements", title="Engagement by Platform", color="platform")

    campaign = df.groupby("campaign", as_index=False)[["clicks", "conversions"]].sum()
    fig_campaign = px.bar(campaign, x="campaign", y=["clicks", "conversions"], barmode="group", title="Campaign Clicks and Conversions")

    posts = df.copy()
    posts["engagements"] = posts["likes"] + posts["comments"] + posts["shares"]
    top_posts = posts.nlargest(5, "engagements")[["date", "platform", "campaign", "engagements"]].copy()
    top_posts["date"] = top_posts["date"].dt.strftime("%Y-%m-%d").fillna("N/A")

    return jsonify({
        "kpis": {
            "visitors": total_visitors,
            "page_views": total_views,
            "engagements": total_engagements,
            "engagement_rate": engagement_rate,
            "clicks": total_clicks,
            "conversions": total_conversions,
            "ctr": ctr
        },
        "traffic_chart": json.loads(plotly.utils.PlotlyJSONEncoder().encode(fig_traffic)),
        "platform_chart": json.loads(plotly.utils.PlotlyJSONEncoder().encode(fig_platform)),
        "campaign_chart": json.loads(plotly.utils.PlotlyJSONEncoder().encode(fig_campaign)),
        "top_posts": top_posts.to_dict(orient="records"),
        "rows": len(df)
    })

@app.route("/upload", methods=["POST"])
def upload_csv():
    file = request.files.get("file")
    if not file or not file.filename.lower().endswith(".csv"):
        return jsonify({"error": "Please choose a CSV file."}), 400
    try:
        df = pd.read_csv(file)
        missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
        if missing:
            return jsonify({"error": "CSV is missing required columns: " + ", ".join(missing)}), 400
        df = df[REQUIRED_COLUMNS]
        df.to_csv(DATA_FILE, index=False)
        return jsonify({"message": f"Uploaded successfully. Loaded {len(df)} rows."})
    except Exception as exc:
        return jsonify({"error": f"Could not read CSV: {exc}"}), 400

@app.route("/download")
def download_csv():
    df = load_data()
    output = BytesIO()
    output.write(df.to_csv(index=False).encode("utf-8"))
    output.seek(0)
    return send_file(output, mimetype="text/csv", as_attachment=True, download_name="marketing_report.csv")

if __name__ == "__main__":
    if not os.path.exists(DATA_FILE):
        create_sample_data()
    app.run(debug=True)
