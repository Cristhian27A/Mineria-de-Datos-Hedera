"""
Módulo de Configuración de Celery
Inicializa la aplicación Celery y configura el Broker y Backend.
"""

from celery import Celery
import os

# Configuración de URLs de Redis
REDIS_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
REDIS_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

# Inicialización de la app Celery
app = Celery(
    "btcusd_analysis_pipeline",
    broker=REDIS_BROKER_URL,
    backend=REDIS_RESULT_BACKEND,
    include=["tasks"]
)

# Configuración con compatibilidad RESP2 para Redis 5.0 en Windows
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1800,
    task_soft_time_limit=1500,
    worker_concurrency=4,
    result_expires=86400,
    # Forzar el protocolo RESP2 compatible con Redis 5.0.14
    broker_transport_options={'protocol': 2},
    result_backend_transport_options={'protocol': 2},
)

if __name__ == "__main__":
    app.start()