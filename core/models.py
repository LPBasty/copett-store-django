from django.db import models
from django.contrib.auth.models import User

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.IntegerField(help_text="Precio del producto")
    descripcion = models.TextField()
    icono = models.CharField(max_length=10, help_text="Emoji temporal", blank=True, null=True)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True, help_text="Foto real de la botella")
    es_vip = models.BooleanField(default=False)

    orden = models.IntegerField(default=0, help_text="0 es el primero. Usa números mayores para enviarlo al final.")

    class Meta:
        # Ordena primero por el campo 'orden' de menor a mayor.
        # Si dos productos tienen el mismo número (ej: ambos son 0), desempata usando el ID.
        ordering = ['orden', 'id']

    def __str__(self):
        tipo = "💎 VIP" if self.es_vip else "🍺 Básico"
        return f"[{self.orden}] {tipo} | {self.nombre}"

class Carrito(models.Model):
    # Relación 1 a 1: Un usuario tiene un solo carrito activo. 
    # null=True permite que en el futuro agreguemos carritos para usuarios "invitados" sin cuenta
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='carrito')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Carrito"
        verbose_name_plural = "Carritos"

    def __str__(self):
        return f"Carrito de {self.usuario.username if self.usuario else 'Invitado'}"

    # Método profesional para calcular el total exacto consultando a los items
    @property
    def total_carrito(self):
        return sum(item.subtotal for item in self.items.all())


class ItemCarrito(models.Model):
    # Relación muchos a uno: Muchos items pertenecen a un solo carrito
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    agregado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Item del Carrito"
        verbose_name_plural = "Items del Carrito"
        # Evita que el mismo producto se agregue dos veces en líneas separadas
        unique_together = ('carrito', 'producto') 

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"

    # Calcula el subtotal multiplicando la cantidad por el precio actual del producto
    @property
    def subtotal(self):
        return self.producto.precio * self.cantidad