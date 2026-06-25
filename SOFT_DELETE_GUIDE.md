# Guía de Soft Delete en GAFRA

## ¿Qué es Soft Delete?

En lugar de **eliminar datos físicamente** de la base de datos, el sistema marca los registros como "eliminados" pero los mantiene. Esto tiene beneficios:

✅ Los datos relacionados permanecen intactos (ej: si eliminas un cliente, sus ventas siguen existiendo)  
✅ Auditoría completa: puedes ver qué fue eliminado y cuándo  
✅ Posibilidad de restaurar datos eliminados por error  
✅ No se pierden registros históricos

## Cómo funciona

### Base de datos

Cada modelo con soft delete tiene dos campos nuevos:
- `deleted` (booleano): `False` = activo, `True` = eliminado
- `deleted_at` (timestamp): Cuándo fue marcado como eliminado

### Modelos que usan Soft Delete

Los siguientes modelos heredan de `SoftDeleteModel`:

```
✓ Cliente
✓ Venta & DetalleVenta
✓ Producto & Receta & ProductoMovimiento
✓ Proveedor
✓ MateriaPrima & MovimientoMateriaPrima
✓ OrdenProduccion & ProduccionDiaria
```

## Comportamiento en la interfaz

### Al eliminar un cliente:

```
ANTES (problema):
- Eliminas Cliente "Juan"
- Las Ventas de Juan desaparecen de la BD
- El historial se pierda

AHORA (solución):
- Eliminas Cliente "Juan"  
- Juan se marca como (ELIMINADO) pero permanece en BD
- Sus Ventas siguen referen a "Juan (ELIMINADO)"
- Auditoría completa preservada
```

### Vistas en admin/panel:

- Los registros eliminados NO aparecen por defecto en listados
- Cuando ves una venta, si el cliente está eliminado, aún puedes ver su nombre con la etiqueta "(ELIMINADO)"

## API para desarrolladores

```python
# Obtener solo activos (por defecto)
clientes = Cliente.objects.all()  # Solo deleted=False

# Obtener incluyendo eliminados
clientes = Cliente.objects.all_including_deleted()

# Obtener solo eliminados
clientes = Cliente.objects.deleted_only()

# En un objeto específico
cliente = Cliente.objects.get(id=1)

# Eliminar (soft delete)
cliente.delete()  # Marca como deleted=True, deleted_at=now()

# Restaurar
cliente.restore()  # Marca como deleted=False, deleted_at=None

# Eliminar físicamente (no recomendado)
cliente.hard_delete()  # Borra permanentemente de la BD
```

## Impacto en relaciones

### Cambios en Foreign Keys

Las relaciones que tenían `CASCADE` (eliminar dependencias) fueron cambiadas a `PROTECT`:

```
ANTES (peligroso):
Proveedor → MateriaPrima (CASCADE)
Si eliminas proveedor → todas sus materias primas se borran

AHORA (seguro):
Proveedor → MateriaPrima (PROTECT)
Si eliminas proveedor → las materias primas permanecen pero el proveedor está marcado como eliminado
```

## Consultas en vistas

Las vistas automáticamente filtran `deleted=False` gracias al Manager personalizado:

```python
# En ListViews, DetailViews, etc.
class ClienteListView(ListView):
    model = Cliente
    # Ya excluye deleted=True automáticamente
    
# Si necesitas ver eliminados:
def admin_audit_view(request):
    all_clients = Cliente.objects.all_including_deleted()
```

## Migración exitosa

Se crearon migraciones para agregar campos `deleted` y `deleted_at` a:
- clientes, productos, proveedores, ventas
- inventario, produccion, usuario

Todas migradas correctamente ✓

## Próximos pasos opcionales

Si necesitas:
1. **Vista de papelera**: Mostrar eliminados y permitir restaurar
2. **Auditoría**: Registrar quién eliminó y cuándo
3. **Limpieza**: Script para eliminar físicamente después de 90 días
4. **Reportes**: Incluir datos eliminados en análisis históricos

Déjame saber si necesitas cualquiera de estas funciones.
