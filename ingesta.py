import mysql.connector
import csv
import boto3
import os
import time
import sys

def connect_to_db(max_retries=30, delay=2):
    """
    Intenta conectarse a MySQL con reintentos
    """
    host = os.getenv('MYSQL_HOST', 'mysql')
    user = os.getenv('MYSQL_USER', 'mi_usuario')
    password = os.getenv('MYSQL_PASSWORD', 'mi_contraseña')
    database = os.getenv('MYSQL_DATABASE', 'mi_base')
    port = int(os.getenv('MYSQL_PORT', 3306))
    
    print(f"🔗 Intentando conectar a MySQL en {host}:{port}")
    
    for attempt in range(max_retries):
        try:
            conn = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                connection_timeout=10
            )
            print(f"✅ Conexión exitosa a MySQL en el intento {attempt + 1}")
            return conn
            
        except mysql.connector.Error as e:
            print(f"❌ Intento {attempt + 1}/{max_retries} falló: {e}")
            if attempt < max_retries - 1:
                print(f"⏳ Esperando {delay} segundos antes del siguiente intento...")
                time.sleep(delay)
            else:
                print("💥 No se pudo conectar a MySQL después de todos los intentos")
                sys.exit(1)

# Establecer conexión con reintentos
conn = connect_to_db()

try:
    print("✅ Conectado a MySQL desde Docker Compose")
    
    cursor = conn.cursor()
    
    # Consultar productos
    print("📊 Consultando tabla productos...")
    cursor.execute("SELECT * FROM productos")
    rows = cursor.fetchall()
    
    print(f"📈 Se encontraron {len(rows)} registros")
    
    # Crear archivo CSV
    csv_file = "productos.csv"
    print(f"📝 Creando archivo CSV: {csv_file}")
    
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        # Escribir encabezados
        writer.writerow([i[0] for i in cursor.description])
        # Escribir datos
        writer.writerows(rows)
    
    print(f"✅ Archivo CSV creado exitosamente con {len(rows)} registros")
    
    # Subir a S3
    print("☁️ Conectando a AWS S3...")
    s3 = boto3.client("s3")
    bucket_name = "dataj-storage-s2"
    s3_key = "ingesta/" + csv_file
    
    print(f"⬆️ Subiendo archivo a S3: s3://{bucket_name}/{s3_key}")
    s3.upload_file(csv_file, bucket_name, s3_key)
    
    print(f"🎉 Archivo {csv_file} subido exitosamente a S3 en bucket {bucket_name}")
    print(f"🔗 Ubicación: s3://{bucket_name}/{s3_key}")

except mysql.connector.Error as db_error:
    print(f"❌ Error de base de datos: {db_error}")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Error durante la ejecución: {e}")
    sys.exit(1)
    
finally:
    # Cerrar conexiones
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals() and conn.is_connected():
        conn.close()
        print("🔌 Conexión a MySQL cerrada")
        
print("🏁 Proceso de ingesta completado exitosamente")