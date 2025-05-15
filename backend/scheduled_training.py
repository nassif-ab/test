import time
import subprocess
import logging
import schedule
from datetime import datetime

# Configurar el logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scheduled_training.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("ScheduledTraining")

def run_training():
    """Ejecuta el script de entrenamiento del sistema de recomendación"""
    logger.info(f"Iniciando entrenamiento programado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        result = subprocess.run(
            ["python", "train_recommendation_system.py"], 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0:
            logger.info("Entrenamiento completado exitosamente")
            logger.info(f"Salida: {result.stdout}")
        else:
            logger.error(f"Error durante el entrenamiento: {result.stderr}")
    except Exception as e:
        logger.error(f"Excepción durante el entrenamiento: {str(e)}")

def main():
    logger.info("Iniciando servicio de entrenamiento programado")
    
    # Ejecutar el entrenamiento inmediatamente al iniciar
    run_training()
    
    # Programar el entrenamiento para ejecutarse cada 5 minutos (para pruebas)
    schedule.every(5).minutes.do(run_training)
    
    # Comentado para pruebas
    # Programar el entrenamiento para ejecutarse cada 12 horas
    # schedule.every(12).hours.do(run_training)
    
    # Programar el entrenamiento para ejecutarse a las 3:00 AM todos los días
    # schedule.every().day.at("03:00").do(run_training)
    
    # Bucle principal para mantener el programa en ejecución
    while True:
        schedule.run_pending()
        time.sleep(60)  # Verificar cada minuto si hay tareas pendientes

if __name__ == "__main__":
    main()
