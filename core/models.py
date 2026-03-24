from django.db import models
from django.contrib.auth.models import User

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.IntegerField(help_text="Precio del producto")
    descripcion = models.TextField()
    icono = models.CharField(max_length=10, help_text="Emoji temporal", blank=True, null=True)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True, help_text="Foto real de la botella")
    es_vip = models.BooleanField(default=False)
    categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE, related_name='productos', null=True, blank=True)
    orden = models.IntegerField(default=0, help_text="0 es el primero. Usa números mayores para enviarlo al final.")
    stock = models.IntegerField(default=0, help_text="Unidades disponibles en bodega")

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


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Proveedor(models.Model):
    empresa = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return self.empresa
    
# ==========================================
# MODELOS DE ÓRDENES (HISTORIAL DE COMPRAS)
# ==========================================

class Pedido(models.Model):
    ESTADOS = (
        ('PENDIENTE', 'Pendiente de Pago'),
        ('PAGADO', 'Pagado - Preparando'),
        ('ENVIADO', 'Enviado al cliente'),
        ('ENTREGADO', 'Entregado'),
    )
    
    # Relación: Un usuario puede tener muchos pedidos
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    
    # Total exacto pagado en ese momento
    total_pagado = models.IntegerField(default=0)
    
    # Datos de envío
    direccion_envio = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-fecha_creacion'] # Los más recientes primero

    def __str__(self):
        return f"Pedido #{self.id} | {self.usuario.username} | {self.get_estado_display()}"


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    
    # TRUCO PRO: 
    # on_delete=models.SET_NULL. Esto hace que si se borra un item de la base de datos, el historial de compras del cliente 
    # no explotará, simplemente dirá "Producto eliminado".
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    
    # El nombre y precio congelados en el tiempo
    nombre_historico = models.CharField(max_length=100)
    precio_historico = models.IntegerField()
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.cantidad}x {self.nombre_historico} (Pedido #{self.pedido.id})"

    @property
    def subtotal(self):
        return self.precio_historico * self.cantidad
    

