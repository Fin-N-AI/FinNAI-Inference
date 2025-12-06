from fastapi import FastAPI
from web.api.routers import company_controller, data_controller, market_controller, report_controller, process_controller

app = FastAPI()

app.include_router(company_controller.router)
app.include_router(data_controller.router)
app.include_router(market_controller.router)
app.include_router(report_controller.router)
app.include_router(process_controller.router)


@app.get("/")
async def root():
    return {"message": "FinNAI-Inference API"}
