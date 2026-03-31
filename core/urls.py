from django.urls import path
from . import views

urlpatterns = [
    path('', views.InicioView.as_view(), name='inicio'), 
    path('vip/', views.TiendaVIPView.as_view(), name='tienda_vip'),
    path('registro/', views.RegistroUsuarioView.as_view(), name='registro'),
    path('agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('procesar-compra/', views.procesar_compra, name='procesar_compra'),
    path('perfil/mis-pedidos/', views.MisPedidosView.as_view(), name='mis_pedidos'),
    path('perfil/mis-datos/', views.MisDatosView.as_view(), name='mis_datos'),
    path('producto/<int:pk>/', views.ProductoDetalleView.as_view(), name='producto_detalle'),
    
    # RUTAS CRUD CATEGORIA (/categoria/operacion/)
    path('categoria/leer/', views.CategoriaListView.as_view(), name='categoria_list'),
    path('categoria/crear/', views.CategoriaCreateView.as_view(), name='categoria_crear'),
    path('categoria/editar/<int:pk>/', views.CategoriaUpdateView.as_view(), name='categoria_editar'),
    path('categoria/eliminar/<int:pk>/', views.CategoriaDeleteView.as_view(), name='categoria_eliminar'),

    # RUTAS CRUD PROVEEDOR (/proveedor/operacion/)
    path('proveedor/leer/', views.ProveedorListView.as_view(), name='proveedor_list'),
    path('proveedor/crear/', views.ProveedorCreateView.as_view(), name='proveedor_crear'),
    path('proveedor/editar/<int:pk>/', views.ProveedorUpdateView.as_view(), name='proveedor_editar'),
    path('proveedor/eliminar/<int:pk>/', views.ProveedorDeleteView.as_view(), name='proveedor_eliminar'),
    path('categoria/<int:categoria_id>/', views.productos_por_categoria, name='productos_por_categoria'),
]
