import mysql.connector
import csv
import boto3

# 1. Conexión a MySQL (usa el nombre del servicio en docker-compose)
import os
import mysql.connector

conn = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST", "mysql"),
    user=os.getenv("MYSQL_USER", "mi_usuario"),
    password=os.getenv("MYSQL_PASSWORD", "mi_contraseña"),
    database=os.getenv("MYSQL_DATABASE", "mi_base"),
    port=int(os.getenv("MYSQL_PORT", 3306))
)

print("✅ Conectado a MySQL desde Docker Compose")

cursor = conn.cursor()

cursor.execute("SELECT * FROM productos")
rows = cursor.fetchall()

csv_file = "productos.csv"
with open(csv_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([i[0] for i in cursor.description])
    writer.writerows(rows)

s3 = boto3.client("s3")
bucket_name = "dataj-storage-s2"
s3.upload_file(csv_file, bucket_name, "ingesta/" + csv_file)

print(f"Archivo {csv_file} subido a S3 en bucket {bucket_name}")

cursor.close()
conn.close()
