"""Vercel Serverless entry point for Smart Parking App."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "smart_parking_app"))


class handler:
    """Handle HTTP requests from Vercel."""

    def __init__(self):
        pass

    @staticmethod
    def do_GET(environ, start_response):
        """Handle GET requests - serve the landing page."""
        status = "200 OK"
        headers = [
            ("Content-Type", "text/html; charset=utf-8"),
            ("Access-Control-Allow-Origin", "*"),
            ("Cache-Control", "public, max-age=0, must-revalidate"),
        ]
        start_response(status, headers)

        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Parking | AI-Driven Occupancy Prediction</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #ffffff;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            color: #1e293b;
            padding: 20px;
        }
        .container { max-width: 680px; text-align: center; padding: 40px; }
        h1 {
            font-size: 2.4rem;
            font-weight: 800;
            background: linear-gradient(135deg, #4F46E5, #6366F1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 16px;
        }
        p { font-size: 1.1rem; color: #64748b; line-height: 1.7; margin-bottom: 32px; }
        .btn {
            display: inline-block;
            padding: 14px 36px;
            background: linear-gradient(135deg, #4F46E5, #6366F1);
            color: #fff;
            font-weight: 700;
            font-size: 1rem;
            border-radius: 999px;
            text-decoration: none;
            box-shadow: 0 4px 24px rgba(79, 70, 229, 0.35);
            transition: all 0.2s ease; border: none; cursor: pointer;
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 8px 32px rgba(79, 70, 229, 0.5); }
        .btn-secondary {
            display: inline-block; margin-left: 12px;
            padding: 13px 32px;
            background: #f1f5f9; color: #475569;
            font-weight: 700; font-size: 1rem;
            border-radius: 999px; text-decoration: none;
            border: 1.5px solid #e2e8f0;
            transition: all 0.2s ease;
        }
        .btn-secondary:hover { background: #e2e8f0; border-color: #cbd5e1; }
        .badge {
            display: inline-block; padding: 6px 16px;
            background: rgba(99, 102, 241, 0.1); color: #4F46E5;
            font-weight: 700; font-size: 0.8rem;
            border-radius: 999px; border: 1px solid rgba(99, 102, 241, 0.2);
            margin-top: 24px;
        }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 32px 0; text-align: left; }
        .card {
            padding: 18px; background: #f8fafc; border-radius: 14px;
            border: 1px solid #e2e8f0; transition: all 0.2s;
        }
        .card:hover { border-color: #818cf8; box-shadow: 0 4px 12px rgba(99,102,241,0.1); }
        .card-icon { font-size: 1.6rem; margin-bottom: 6px; }
        .card-title { font-weight: 700; font-size: 0.9rem; margin-bottom: 4px; color: #1e293b; }
        .card-desc { font-size: 0.8rem; color: #64748b; }
        .footer { margin-top: 32px; font-size: 0.8rem; color: #94a3b8; }
        @media (max-width: 480px) { .grid { grid-template-columns: 1fr; } h1 { font-size: 1.6rem; } }
    </style>
</head>
<body>
    <div class="container">
        <div style="font-size: 3rem; margin-bottom: 16px;">🅿️</div>
        <h1>AI-Driven Smart<br/>Occupancy Prediction</h1>
        <p>Real-time parking availability powered by satellite GPS telemetry and XGBoost machine learning — always one step ahead.</p>
        <div style="margin-bottom: 24px;">
            <a class="btn" href="https://smartparkingai.streamlit.app" target="_blank">🚀 Launch Full App</a>
            <a class="btn-secondary" href="#learn-more">📖 Learn More</a>
        </div>
        <div class="badge">⚡ Deploy on Streamlit Community Cloud for full interactive experience</div>
        <div class="grid">
            <div class="card">
                <div class="card-icon">🤖</div>
                <div class="card-title">Live ML Predictions</div>
                <div class="card-desc">XGBoost model runs real-time occupancy inference</div>
            <div class="card">
                <div class="card-icon">🗺️</div>
                <div class="card-title">Google Maps</div>
                <div class="card-desc">Interactive parking lot map with directions</div>
            <div class="card">
                <div class="card-icon">🎫</div>
                <div class="card-title">QR Check-In</div>
                <div class="card-desc">Contactless entry via scannable QR codes</div>
            <div class="card">
                <div class="card-icon">📡</div>
                <div class="card-title">GPS Telemetry</div>
                <div class="card-desc">Satellite-based occupancy estimation</div>
        </div>
        <div class="footer">
            Built with Streamlit · AI model: XGBoost · GPS: NAVSTAR + GLONASS<br/>
            © 2026 Smart Parking · AI-Powered Platform
        </div>
</body>
</html>"""
        return [html.encode("utf-8")]

    @staticmethod
    def do_POST(environ, start_response):
        return handler.do_GET(environ, start_response)

    @staticmethod
    def do_HEAD(environ, start_response):
        status = "200 OK"
        headers = [("Content-Type", "text/html; charset=utf-8")]
        start_response(status, headers)
        return [b""]


# WSGI application for Vercel
def app(environ, start_response):
    method = environ.get("REQUEST_METHOD", "GET")
    if method == "POST":
        return handler.do_POST(environ, start_response)
    elif method == "HEAD":
        return handler.do_HEAD(environ, start_response)
    else:
        return handler.do_GET(environ, start_response)
