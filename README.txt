Digital Marketing Analytics Dashboard

1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Run: python -m venv .venv
4. Windows: .venv\\Scripts\\activate
   macOS/Linux: source .venv/bin/activate
5. Run: python -m pip install -r requirements.txt
6. Run: python app.py
7. Open http://127.0.0.1:5000 in your browser.

CSV upload requires these columns:
date, visitors, page_views, platform, likes, comments, shares, campaign, clicks, conversions, spend

The included data is synthetic sample data for demonstration. The dashboard uses a simple engagement-rate proxy based on visitors, and CTR based on clicks/page views; these definitions may differ from platform-native metrics.
