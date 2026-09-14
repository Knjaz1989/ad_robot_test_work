from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.logic import get_demo_data, build_page_html


fast_app = FastAPI()


@fast_app.get("/ping")
def ping():
    return {"message": "pong"}


@fast_app.get("/graph", response_class=HTMLResponse)
def show_graph():
    dates, cost, cpa, roi_confirmed, conversions = get_demo_data()
    return build_page_html(dates, cost, cpa, roi_confirmed, conversions)
