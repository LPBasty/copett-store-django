from django.contrib import admin
from .models import Producto
from .models import Producto, Carrito, ItemCarrito


# Configuración personalizada para el panel
class ProductoAdmin(admin.ModelAdmin):

    list_display = ['nombre', 'es_vip', 'precio', 'orden']
    # Permite editar el campo 'orden' directamente desde la lista
    list_editable = ['orden'] 
    list_filter = ['es_vip']
    search_fields = ['nombre']

# Registramos el modelo conectado a esta nueva configuración
admin.site.register(Producto, ProductoAdmin)

# Configuración personalizada para el carrito y sus items
class ItemCarritoInline(admin.TabularInline):
    model = ItemCarrito
    extra = 0 # No mostrar filas vacías por defecto

class CarritoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'creado_en', 'actualizado_en']
    inlines = [ItemCarritoInline] # Muestra los items directamente dentro de la vista del carrito

admin.site.register(Carrito, CarritoAdmin)
admin.site.register(ItemCarrito)