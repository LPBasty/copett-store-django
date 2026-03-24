# actividad_m7_15/consultas_ORM

from core.models import Producto, Proveedor
from django.db import connection
from django.db.models import Count

# ==========================================
# 1. Recuperación de registros
# ==========================================

# Recupera todos los productos registrados.
todos_los_productos = Producto.objects.all()

# Recupera solo los productos cuyo proveedor sea "CCU" en reemplazo del autor).
productos_destileria = Producto.objects.filter(proveedor__nombre="CCU")

# Recupera los productos que tienen más de 20 unidades en stock (adaptación de las más de 200 páginas).
productos_alto_stock = Producto.objects.filter(stock__gt=20)


# ==========================================
# 2. Filtros y exclusiones
# ==========================================

# Aplica un filtro para mostrar solo productos disponibles en la tienda.
productos_disponibles = Producto.objects.filter(disponible=True)

# Excluye todos los productos que tengan menos de 10 unidades de stock.
productos_sin_bajo_stock = Producto.objects.exclude(stock__lt=10)


# ==========================================
# 3. Consultas personalizadas con SQL
# ==========================================

# Ejecuta una consulta SQL directa utilizando raw() para obtener todos los productos ordenados por nombre.
productos_raw = Producto.objects.raw("SELECT * FROM core_producto ORDER BY nombre;")

# Usa connection.cursor() para ejecutar una query personalizada (conteo de productos por proveedor) y mostrar los resultados.
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT prov.nombre, COUNT(prod.id)
        FROM core_proveedor prov
        JOIN core_producto prod ON prov.id = prod.proveedor_id
        GROUP BY prov.nombre;
    """)
    resultados = cursor.fetchall()
    for fila in resultados:
        print(f"Proveedor: {fila[0]}, Total Productos: {fila[1]}")


# ==========================================
# 4. Campos específicos y anotaciones
# ==========================================

# Recupera solo los nombres (títulos) de todos los productos usando values().
nombres_productos = Producto.objects.values('nombre')
# Alternativa con only(): Producto.objects.only('nombre')

# Agrega una anotación (usando annotate) para contar cuántos productos hay por proveedor.
productos_por_proveedor = Proveedor.objects.annotate(total_productos=Count('producto'))