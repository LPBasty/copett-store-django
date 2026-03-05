from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Producto, Carrito, ItemCarrito

class RegistroUsuarioView(CreateView):
    template_name = 'core/registro.html'
    
    form_class = UserCreationForm 
    
    success_url = reverse_lazy('login')

    # EL PORTERO: Intercepta la petición antes de cargar la página
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, f"Hola {request.user.username}, ya tienes una sesión iniciada en el Club.")
            return redirect('inicio') # Lo mandamos a la página principal
        
        # Si no está logueado, lo deja pasar normalmente
        return super().dispatch(request, *args, **kwargs)

# 1. Vista Pública: Filtramos solo los que NO son VIP
class InicioView(ListView):
    model = Producto
    template_name = 'core/inicio.html'
    context_object_name = 'productos' # En la plantilla, usaremos 'productos' para referirnos a la lista que trae esta vista
    def get_queryset(self):
        # Vamos a la BD y traemos solo los básicos
        return Producto.objects.filter(es_vip=False)

# 2. Vista Protegida: Filtramos solo los que SÍ son VIP
class TiendaVIPView(LoginRequiredMixin, ListView):
    model = Producto
    template_name = 'core/vip.html'
    context_object_name = 'productos_vip'

    def get_queryset(self):
        return Producto.objects.filter(es_vip=True)

# Vista de panel de usuario

@login_required(login_url='login')
def agregar_al_carrito(request, producto_id):
    # 1. Buscamos el producto en la BD. Si alteran la URL con un ID falso, tira error 404.
    producto = get_object_or_404(Producto, id=producto_id)
    
    # 2. Obtenemos o creamos el carrito del usuario logueado
    carrito, creado = Carrito.objects.get_or_create(usuario=request.user)
    
    # 3. Verificamos si el producto ya está en el carrito
    item, item_creado = ItemCarrito.objects.get_or_create(carrito=carrito, producto=producto)
    
    if not item_creado:
        # Si ya existía, aumentamos la cantidad
        item.cantidad += 1
        item.save()
        messages.success(request, f'Se aumentó la cantidad de {producto.nombre} en tu copa.')
    else:
        # Si es nuevo, se guarda con cantidad 1 por defecto
        messages.success(request, f'{producto.nombre} fue añadido a tu copa.')
        
    # 4. Redirigimos al usuario a la misma página donde estaba comprando
    # (Para no enviarlo a la página de inicio si estaba en la sección VIP)
    return redirect(request.META.get('HTTP_REFERER', 'inicio'))

@login_required(login_url='login')
def ver_carrito(request):
    try:
        # Buscamos el carrito del usuario logueado
        carrito = Carrito.objects.get(usuario=request.user)
    except Carrito.DoesNotExist:
        # Si no tiene carrito, pasamos None
        carrito = None
        
    return render(request, 'core/carrito.html', {'carrito': carrito})

@login_required(login_url='login')
def eliminar_del_carrito(request, item_id):
    # Buscamos el item. Validamos que pertenezca al carrito del usuario actual por seguridad
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    
    if item.cantidad > 1:
        # Si hay más de 1, restamos 1
        item.cantidad -= 1
        item.save()
        messages.info(request, f'Se restó una unidad de {item.producto.nombre}.')
    else:
        # Si solo hay 1, eliminamos la fila completa de la base de datos
        item.delete()
        messages.error(request, f'{item.producto.nombre} fue eliminado de tu copa.')
        
    return redirect('ver_carrito')


"""EJERCICIO PRÁCTICO DE ORM - VISTA DE PRUEBA

def ejercicio_orm(request):

    html_response = "<h1>Resultados del Ejercicio ORM</h1>"

    # 1. CREAR (Create)
    nuevo_producto = Producto.objects.create(
    nombre="Ron Mítico de Prueba",
    precio=45000,
    descripcion="Botella creada desde la vista de práctica.",
    es_vip=True,
    orden=10
    )
    html_response += f"<p><b>Creado:</b> {nuevo_producto.nombre} (ID: {nuevo_producto.id})</p>"

    # 2. SELECCIONAR (Select All)
    todos = Producto.objects.all()
    html_response += f"<p> <b>Seleccionados:</b> Hay {todos.count()} productos en total en la tienda.</p>"

    # 3. FILTRAR (Filter)
    caros = Producto.objects.filter(precio__gt=20000) # Trae solo los productos cuyo precio es mayor a $20.000
    html_response += f"<p> <b>Filtrados:</b> Encontré {caros.count()} productos que cuestan más de $20.000.</p>"

    # 4. EXCLUIR (Exclude)
    clasicos = Producto.objects.exclude(es_vip=True) # Trae solo los productos que NO son VIP (es decir, los básicos)
    html_response += f"<p><b>Excluidos:</b> Tenemos {clasicos.count()} productos que NO son VIP.</p>"

    # 5. ORDENAR (Order By)
    mas_caros_primero = Producto.objects.all().order_by('-precio')
    html_response += f"<p> <b>Ordenados:</b> El producto más caro de la tienda es '{mas_caros_primero.first().nombre}' a ${mas_caros_primero.first().precio}.</p>"

    # 6. ACTUALIZAR (Update)
    Producto.objects.filter(id=nuevo_producto.id).update(precio=50000) # Actualiza el precio del producto que creamos al principio a $50.000. Usamos filter para no correr el riesgo de actualizar varios productos a la vez.
    html_response += f"<p> <b>Actualizado:</b> El precio del producto ID {nuevo_producto.id} subió a $50.000.</p>"

    # 7. ELIMINAR (Delete)
    producto_a_borrar = Producto.objects.get(id=nuevo_producto.id)
    producto_a_borrar.delete() # Elimina el producto que creamos al principio. Usamos get porque es un solo producto específico.
    html_response += f"<p> <b>Eliminado:</b> El producto ID {nuevo_producto.id} fue destruido correctamente.</p>"

    return HttpResponse(html_response)"""

