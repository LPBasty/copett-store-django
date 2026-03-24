from django.contrib import admin
from .models import Categoria, Producto, Proveedor
from .models import Producto, Carrito, ItemCarrito, Pedido, ItemPedido


# Configuración personalizada para el panel
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'stock', 'es_vip', 'precio', 'orden']
    
    list_editable = ['orden', 'categoria', 'stock'] 
    
    list_filter = ['es_vip', 'categoria']
    
    search_fields = ['nombre']

admin.site.register(Producto, ProductoAdmin)

class ItemCarritoInline(admin.TabularInline):
    model = ItemCarrito
    extra = 0 # No mostrar filas vacías por defecto

class CarritoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'creado_en', 'actualizado_en']
    inlines = [ItemCarritoInline] # Muestra los items directamente dentro de la vista del carrito

admin.site.register(Carrito, CarritoAdmin)
admin.site.register(ItemCarrito)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion')
    search_fields = ('nombre',)
    ordering = ('nombre',)

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('id', 'empresa', 'telefono', 'email')
    search_fields = ('empresa', 'email')
    ordering = ('empresa',)

admin.site.register(Pedido)
admin.site.register(ItemPedido)
