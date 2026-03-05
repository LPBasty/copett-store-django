from django.urls import path
from . import views

urlpatterns = [
    path('', views.InicioView.as_view(), name='inicio'), 
    path('vip/', views.TiendaVIPView.as_view(), name='tienda_vip'),
    path('registro/', views.RegistroUsuarioView.as_view(), name='registro'),
    path('agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    #path('orm-practica/', views.ejercicio_orm, name='ejercicio_orm'),    # RUTA PARA EL EJERCICIO PRÁCTICO
]
