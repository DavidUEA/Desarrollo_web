from typing import List, Dict, Set
from collections import defaultdict
from models import Producto, Categoria
from repository import ProductoRepository, categoriaRepository

class Inventario:
    def __init__(self):
        self.producto_repo = ProductoRepository()
        self.categoria_repo = categoriaRepository()

    def agregar_producto(self, nombre: str, cantidad: int, precio: float, categoria_nombre: str) -> Producto:
        categoria = self.categoria_repo.obtener_por_nombre(categoria_nombre)
        if not categoria:
            categoria = categoria(nombre=categoria_nombre)
            self.categoria_repo.agregar(categoria)
        producto = Producto(nombre=nombre, precio=precio, categoria=categoria, cantidad=cantidad)
        self.producto_repo.agregar(producto)
        return producto

    def eliminar_producto(self, producto_id: int) -> bool:
        return self.producto_repo.eliminar(producto_id)

    def actualizar_producto(self, producto_id: int, **kwargs) -> bool:
        return self.producto_repo.actualizar(producto_id, **kwargs)
    
    def listar_productos(self) -> List[Producto]:
        return self.producto_repo.listar_todos()

    def buscar_productos_por_categoria(self, categoria_nombre: str) -> List[Producto]:
        categoria = self.categoria_repo.obtener_por_nombre(categoria_nombre)
        if not categoria:
            return []
        return self.producto_repo.buscar_por_categoria(categoria.id)

    def obtener_estadisticas_inventario(self) -> Dict[str, float]:
        Productos = self.producto_repo.listar_todos()
        total_valor = sum(p.precio * p.cantidad for p in Productos)
        return {
            "total_productos": len(Productos),
            "valor_total": total_valor,
            
        }