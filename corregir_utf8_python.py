#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir caracteres UTF-8 en la base de datos
"""
import psycopg2

# Conexión a la base de datos (desde el contenedor, usar el host del contenedor de PostgreSQL)
conn = psycopg2.connect(
    host='db',
    port=5432,
    database='defensoria_db',
    user='defensoria_dev',
    password='defensoria_dev_password'
)

cursor = conn.cursor()

# Datos correctos con UTF-8
datos_correctos = [
    (13, 'Comentarios sobre tráfico vehicular en hora pico - Usuarios reportan demoras de hasta 2 horas en principales vías de acceso', 'Bogotá D.C.'),
    (12, 'Incremento de quejas sobre falta de agua potable en zona rural - 25 familias afectadas sin acceso al recurso vital', 'La Guajira'),
    (14, 'Reportes de amenazas contra líderes sociales en municipio del sur - 8 casos documentados en el último mes', 'Nariño'),
    (15, 'Denuncias sobre desplazamiento forzado - 15 familias abandonan comunidad rural por presencia de grupos armados', 'Cauca'),
    (11, 'Alertas de violencia intrafamiliar en zona urbana - Incremento del 40% en últimas dos semanas según autoridades locales', 'Medellín')
]

print("=" * 80)
print("CORRIGIENDO CARACTERES UTF-8 EN BASE DE DATOS")
print("=" * 80)

for id_senal, contenido, ubicacion in datos_correctos:
    # Actualizar contenido
    cursor.execute(
        "UPDATE senal_detectada SET contenido_detectado = %s WHERE id_senal_detectada = %s",
        (contenido, id_senal)
    )
    
    # Actualizar metadatos con ubicación
    cursor.execute(
        "UPDATE senal_detectada SET metadatos = jsonb_set(COALESCE(metadatos, '{}'::jsonb), '{ubicacion}', to_jsonb(%s::text)) WHERE id_senal_detectada = %s",
        (ubicacion, id_senal)
    )
    
    print(f"✓ Actualizado ID {id_senal}: {ubicacion}")

# Commit
conn.commit()

# Verificar
print("\n" + "=" * 80)
print("VERIFICACIÓN:")
print("=" * 80)

cursor.execute("""
    SELECT 
        id_senal_detectada,
        contenido_detectado,
        metadatos->>'ubicacion' as ubicacion
    FROM senal_detectada 
    WHERE id_senal_detectada IN (11, 12, 13, 14, 15)
    ORDER BY id_senal_detectada
""")

for row in cursor.fetchall():
    id_senal, contenido, ubicacion = row
    print(f"\nID {id_senal}:")
    print(f"  Ubicación: {ubicacion}")
    print(f"  Contenido: {contenido[:80]}...")

cursor.close()
conn.close()

print("\n" + "=" * 80)
print("✅ CORRECCIÓN COMPLETADA")
print("=" * 80)
