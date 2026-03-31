from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Producto, Carrito, ItemCarrito, Pedido, ItemPedido
from .models import Categoria, Proveedor
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.models import User
from .forms import UserUpdateForm # Tu nuevo formulario

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
# 1. Vista Principal Inteligente (Catálogo y Búsqueda Global)
class InicioView(ListView):
    model = Producto
    template_name = 'core/inicio.html'
    context_object_name = 'productos'

    def get_queryset(self):
        # Capturamos si viene una búsqueda de la barra superior
        query = self.request.GET.get('buscar')

        # ==========================================
        # MODO 1: MODO BÚSQUEDA GLOBAL
        # ==========================================
        if query:
            # Buscamos la palabra clave cruzando todas las tablas (Q objects)
            queryset = Producto.objects.filter(
                Q(nombre__icontains=query) | 
                Q(descripcion__icontains=query) |
                Q(categoria__nombre__icontains=query)
            ).distinct()
            
            # EL CANDADO INTELIGENTE: Si el usuario NO está logueado, le ocultamos los resultados VIP
            if not self.request.user.is_authenticated:
                queryset = queryset.filter(es_vip=False)
                
            return queryset

        # ==========================================
        # MODO 2: MODO NAVEGACIÓN NORMAL
        # ==========================================
        # Si la barra de búsqueda está vacía, mostramos el catálogo básico normal
        queryset = Producto.objects.filter(es_vip=False)
        
        # Y aplicamos el filtro de categoría si es que hizo clic en el menú
        categoria_id = self.request.GET.get('categoria')
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
            
        return queryset

# 2. Vista Protegida: Filtramos solo los que SÍ son VIP
class TiendaVIPView(LoginRequiredMixin, ListView):
    model = Producto
    template_name = 'core/vip.html'
    context_object_name = 'productos_vip'

    def get_queryset(self):
        queryset = Producto.objects.filter(es_vip=True)
        
        categoria_id = self.request.GET.get('categoria')
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        
        return queryset

# Vista de panel de usuario

@login_required(login_url='login')

def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    
    #1. SEGURIDAD: ¿El producto está agotado en la base de datos?
    if producto.stock <= 0:
        messages.error(request, f'Lo sentimos, {producto.nombre} se encuentra agotado por el momento.')
        return redirect(request.META.get('HTTP_REFERER', 'inicio'))
    
    carrito, creado = Carrito.objects.get_or_create(usuario=request.user)
    item, item_creado = ItemCarrito.objects.get_or_create(carrito=carrito, producto=producto)
    
    if not item_creado:
        #2. SEGURIDAD: ¿El cliente está intentando agregar más unidades de las que existen?
        if item.cantidad >= producto.stock:
            messages.warning(request, f'Solo nos quedan {producto.stock} unidades de {producto.nombre} en bodega.')
        else:
            item.cantidad += 1
            item.save()
            messages.success(request, f'Se aumentó la cantidad de {producto.nombre} en tu copa.')
    else:
        messages.success(request, f'{producto.nombre} fue añadido a tu copa.')
        
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

# CRUD DE LA TABLA: CATEGORIA

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        # La prueba: ¿Es el usuario un superadministrador (staff)?
        return self.request.user.is_superuser

    def handle_no_permission(self):
        # El castigo: Si un usuario normal (o anónimo) intenta entrar, 
        # lo pateamos de vuelta a la página de inicio silenciosamente.
        return redirect('inicio')


class CategoriaListView(AdminRequiredMixin, ListView):
    model = Categoria
    template_name = 'core/crud/categoria_list.html'
    context_object_name = 'categorias'

class CategoriaCreateView(AdminRequiredMixin, CreateView):
    model = Categoria
    fields = '__all__' # Toma todos los campos del modelo
    template_name = 'core/crud/categoria_form.html'
    success_url = reverse_lazy('categoria_list') # A donde va al guardar

class CategoriaUpdateView(AdminRequiredMixin, UpdateView):
    model = Categoria
    fields = '__all__'
    template_name = 'core/crud/categoria_form.html' # Reutiliza el HTML de crear
    success_url = reverse_lazy('categoria_list')

class CategoriaDeleteView(AdminRequiredMixin, DeleteView):
    model = Categoria
    template_name = 'core/crud/categoria_confirm_delete.html'
    success_url = reverse_lazy('categoria_list')


# CRUD DE LA TABLA: PROVEEDOR

class ProveedorListView(AdminRequiredMixin, ListView):
    model = Proveedor
    template_name = 'core/crud/proveedor_list.html'
    context_object_name = 'proveedores'

class ProveedorCreateView(AdminRequiredMixin, CreateView):
    model = Proveedor
    fields = '__all__'
    template_name = 'core/crud/proveedor_form.html'
    success_url = reverse_lazy('proveedor_list')

class ProveedorUpdateView(AdminRequiredMixin, UpdateView):
    model = Proveedor
    fields = '__all__'
    template_name = 'core/crud/proveedor_form.html'
    success_url = reverse_lazy('proveedor_list')

class ProveedorDeleteView(AdminRequiredMixin, DeleteView):
    model = Proveedor
    template_name = 'core/crud/proveedor_confirm_delete.html'
    success_url = reverse_lazy('proveedor_list')

################ VISTA: PRODUCTOS POR CATEGORÍA ################

def productos_por_categoria(request, categoria_id):
    # 1. Buscamos la categoría exacta o damos error 404 si alteran la URL
    categoria = get_object_or_404(Categoria, id=categoria_id)
    
    # 2. Filtramos los productos que pertenezcan a esa categoría
    # (Usamos el campo 'categoria' que creamos antes como ForeignKey)
    productos_filtrados = Producto.objects.filter(categoria=categoria)
    
    # 3. Enviamos los resultados a una nueva plantilla
    contexto = {
        'categoria': categoria,
        'productos': productos_filtrados
    }
    return render(request, 'core/categoria_productos.html', contexto)

# ==========================================
# PROCESAMIENTO DE ORDEN (CHECKOUT)
# ==========================================
@login_required(login_url='login')
def procesar_compra(request):
    # Solo aceptamos peticiones POST por seguridad (para que no compren recargando la página)
    if request.method == 'POST':
        try:
            carrito = Carrito.objects.get(usuario=request.user)
            items = carrito.items.all()
            
            if not items.exists():
                messages.error(request, "Tu copa está vacía. Agrega licores antes de procesar el pedido.")
                return redirect('inicio')

            # BURBUJA DE SEGURIDAD: Todo o nada
            with transaction.atomic():
                # 1. Creamos la "Boleta" en blanco
                pedido = Pedido.objects.create(
                    usuario=request.user,
                    total_pagado=carrito.total_carrito,
                    estado='PAGADO' # Lo marcamos pagado de inmediato para este ejercicio
                )

                # 2. Traspasamos los licores y congelamos el precio
                for item in items:
                    # Última validación de stock (por si otro cliente compró la última botella hace 5 segundos)
                    if item.producto.stock < item.cantidad:
                        raise ValueError(f"Lo sentimos, alguien acaba de comprar las últimas unidades de {item.producto.nombre}.")
                    
                    ItemPedido.objects.create(
                        pedido=pedido,
                        producto=item.producto,
                        nombre_historico=item.producto.nombre,
                        precio_historico=item.producto.precio,
                        cantidad=item.cantidad
                    )
                    
                    # 3. Descontamos el stock de la bodega real
                    item.producto.stock -= item.cantidad
                    item.producto.save()

                # 4. Destruimos los items del carrito (vaciamos la canasta)
                items.delete()
                
            # Si el código llega aquí, la burbuja atómica fue un éxito
            messages.success(request, f"¡Salud! Tu pedido #{pedido.id} ha sido procesado con éxito. Preparando el envío.")
            return redirect('inicio') 

        except Carrito.DoesNotExist:
            messages.error(request, "No tienes un carrito activo.")
            return redirect('inicio')
        except ValueError as e:
            # Si saltó el error de stock, la transacción se cancela y devolvemos el mensaje al usuario
            messages.error(request, str(e))
            return redirect('ver_carrito')
            
    # Si intentan entrar por la URL sin darle al botón, los rebotamos
    return redirect('ver_carrito')

# ==========================================
# PANEL DE USUARIO (PERFIL)
# ==========================================
class MisPedidosView(LoginRequiredMixin, ListView):
    model = Pedido
    template_name = 'core/mis_pedidos.html'
    context_object_name = 'pedidos'

    def get_queryset(self):
        # Filtramos la tabla histórica de Pedidos para traer SOLO los de este cliente.
        # El order_by('-fecha_creacion') asegura que la compra más reciente salga arriba.
        return Pedido.objects.filter(usuario=self.request.user).order_by('-fecha_creacion')

class MisDatosView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'core/mis_datos.html'
    success_url = reverse_lazy('mis_datos') # Al guardar, recarga la misma página

    def get_object(self):
        # En lugar de buscar un ID en la URL, devolvemos obligatoriamente al usuario actual.
        # Es imposible hackear esto para editar a otro cliente.
        return self.request.user

    def form_valid(self, form):
        # Agregamos un mensaje verde flotante cuando se guarde con éxito
        messages.success(self.request, "¡Tus datos han sido actualizados con éxito!")
        return super().form_valid(form)

# DETALLE DE PRODUCTO Y CROSS-SELLING
# ==========================================
class ProductoDetalleView(DetailView):
    model = Producto
    template_name = 'core/producto_detalle.html'
    context_object_name = 'producto'

    def get_context_data(self, **kwargs):
        # 1. Recuperamos el contexto normal (el producto principal)
        context = super().get_context_data(**kwargs)
        producto_actual = self.object
        
        # 2. EL ALGORITMO DE CROSS-SELLING
        if producto_actual.categoria:
            # Buscamos botellas de la misma categoría, que tengan el mismo nivel de acceso (VIP o Básico),
            # y EXCLUIMOS la botella que el cliente ya está mirando.
            relacionados = Producto.objects.filter(
                categoria=producto_actual.categoria,
                es_vip=producto_actual.es_vip
            ).exclude(id=producto_actual.id).order_by('?')[:3] 
            #order_by('?') selecciona 3 botellas al azar para que la vitrina siempre cambie
        else:
            relacionados = Producto.objects.none()
            
        # 3. Mandamos las recomendaciones al HTML
        context['productos_relacionados'] = relacionados
        return context