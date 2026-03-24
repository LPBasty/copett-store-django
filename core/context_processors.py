from .models import Carrito, Categoria

def total_carrito(request):
    total = 0
    # Solo buscamos el carrito si el usuario inició sesión
    if request.user.is_authenticated:
        try:
            # Buscamos el carrito del usuario
            carrito = Carrito.objects.get(usuario=request.user)
            # Sumamos las cantidades de todos los items (ej: 2 vodkas + 1 ron = 3 ítems)
            total = sum(item.cantidad for item in carrito.items.all())
        except Carrito.DoesNotExist:
            total = 0
            
    # Retorna un diccionario que estará disponible en TODOS los HTML de tu sitio
    return {'cantidad_carrito': total}

def categorias_globales(request):
    return {'categorias_menu': Categoria.objects.all()}
