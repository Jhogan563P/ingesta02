import mysql.connector
import csv
import boto3

# 1. Conexión a MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="utec!",   # la contraseña que configuraste
    database="ingesta_db"
)
cursor = conn.cursor()

# 2. Leer registros de la tabla
cursor.execute("SELECT * FROM productos")
rows = cursor.fetchall()

# 3. Guardar resultados en CSV
csv_file = "productos.csv"
with open(csv_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([i[0] for i in cursor.description])  # encabezados
    writer.writerows(rows)

# 4. Subir CSV a S3
s3 = boto3.client("s3")
bucket_name = "dataj-storage-s2"   # reemplaza con el nombre real
s3.upload_file(csv_file, bucket_name,"ingesta/"+ csv_file)

print(f"Archivo {csv_file} subido a S3 en bucket {bucket_name}")

# 5. Cerrar conexión
cursor.close()
conn.close()
