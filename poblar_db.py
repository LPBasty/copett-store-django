import os
import django

# 1. Configurar el entorno de Django para poder usar la base de datos desde este script
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mi_tienda.settings')
django.setup()

from core.models import Producto

def poblar_base_de_datos():
    print("Iniciando la carga masiva de licores...")

    # Borrar los productos anteriores para no duplicar si corres el script 2 veces (Opcional)
    Producto.objects.all().delete()
    print("Base de datos limpiada.")

    # 2. Creamos una lista con todos los productos que queremos guardar
    lista_productos = [
        # --- 10 PRODUCTOS BÁSICOS (es_vip=False) ---
        Producto(nombre='Cerveza Lager 6-Pack', precio=4500, descripcion='Clásica cerveza rubia, muy refrescante.', icono='🍺', es_vip=False),
        Producto(nombre='Cerveza IPA Artesanal', precio=6500, descripcion='Amargor intenso con notas cítricas y florales.', icono='🍺', es_vip=False),
        Producto(nombre='Vodka Estándar', precio=7990, descripcion='Destilado puro, ideal para coctelería y mezclas.', icono='🍸', es_vip=False),
        Producto(nombre='Ron Añejo Especial', precio=6500, descripcion='Sabor suave con notas de vainilla y caramelo.', icono='🍹', es_vip=False),
        Producto(nombre='Pisco Reservado 40°', precio=5990, descripcion='Perfecto para la piscola del fin de semana.', icono='🧊', es_vip=False),
        Producto(nombre='Vino Cabernet Sauvignon', precio=4200, descripcion='Vino tinto joven del Valle Central.', icono='🍷', es_vip=False),
        Producto(nombre='Vino Sauvignon Blanc', precio=4500, descripcion='Vino blanco fresco y frutal.', icono='🥂', es_vip=False),
        Producto(nombre='Whisky 3 Años', precio=9990, descripcion='Blend escocés tradicional y muy versátil.', icono='🥃', es_vip=False),
        Producto(nombre='Tequila Reposado', precio=12500, descripcion='Suave tequila mexicano ideal para margaritas.', icono='🍋', es_vip=False),
        Producto(nombre='Gin Clásico London Dry', precio=11000, descripcion='Base perfecta para un Gin Tonic tradicional.', icono='🍸', es_vip=False),

        # --- 10 PRODUCTOS VIP (es_vip=True) ---
        Producto(nombre='Whisky Single Malt 18 Años', precio=85000, descripcion='Añejado en barricas de roble europeo. Notas a madera y humo.', icono='🥃', es_vip=True),
        Producto(nombre='Whisky Blue Label Premium', precio=210000, descripcion='La mezcla más exclusiva y extraordinaria de Escocia.', icono='🥃', es_vip=True),
        Producto(nombre='Vodka Premium Ruso', precio=45000, descripcion='Filtrado 5 veces con cuarzo y carbón de abedul.', icono='🍸', es_vip=True),
        Producto(nombre='Champagne Francés Vintage', precio=120000, descripcion='Cosecha excepcional con burbuja fina y persistente.', icono='🍾', es_vip=True),
        Producto(nombre='Tequila Añejo Cristalino', precio=60000, descripcion='100% Agave azul, extrema suavidad y elegancia.', icono='🥂', es_vip=True),
        Producto(nombre='Cognac XO Reserve', precio=150000, descripcion='Mezcla de los mejores aguardientes de uva francesa.', icono='🥃', es_vip=True),
        Producto(nombre='Vino Ícono Valle de Colchagua', precio=95000, descripcion='Ensamblaje tinto de calidad mundial, ganador de premios.', icono='🍷', es_vip=True),
        Producto(nombre='Gin Botánico Ultra Premium', precio=48000, descripcion='Destilado con 47 botánicos seleccionados a mano.', icono='🍸', es_vip=True),
        Producto(nombre='Ron Gran Reserva 21 Años', precio=75000, descripcion='Añejamiento prolongado, notas a cacao y tabaco dulce.', icono='🍹', es_vip=True),
        Producto(nombre='Pisco Premium Envejecido', precio=35000, descripcion='Doble destilado reposado en barricas de roble americano.', icono='🧊', es_vip=True),
    ]

    # 3. ¡LA MAGIA! bulk_create guarda toda la lista en la BD en una sola operación
    Producto.objects.bulk_create(lista_productos)
    
    print(f"¡Éxito! Se han creado {len(lista_productos)} productos en la base de datos.")

if __name__ == '__main__':
    poblar_base_de_datos()