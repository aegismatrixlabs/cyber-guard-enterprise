from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging

# Kurumsal loglama yapılandırması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CyberGuardCore")

app = FastAPI(
    title="CyberGuard Enterprise SOC API",
    version="1.0.0",
    description="Core backend infrastructure for autonomous threat detection and SOC operations."
)

# Güvenli CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production ortamında spesifik domainler ile sınırlandırılacaktır
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Sistem iç detaylarının ve hassas stack trace'lerin sızmasını önleyen global güvenlik kalkanı.
    """
    logger.error(f"Kritik hata yakalandı [{request.url}]: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal server error occurred. Security team has been notified."
        }
    )

@app.get("/api/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Sistem altyapısının ve API servisinin ayakta olduğunu doğrulayan sağlık kontrolü uç noktası.
    """
    try:
        return {
            "success": True,
            "status": "healthy",
            "service": "CyberGuard Enterprise SOC",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check hatası: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"success": False, "error": "Service unhealthy"}
        )

if __name__ == "__main__":
    import uvicorn
    try:
        uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
    except Exception as e:
        logger.critical(f"Sunucu başlatılamadı: {str(e)}")
