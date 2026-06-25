# Mixin para implementar soft delete en modelos Django
from django.db import models
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    """QuerySet que filtra objetos eliminados por defecto"""
    
    def delete(self):
        """Marca como eliminado en lugar de borrar físicamente"""
        return self.update(deleted=True, deleted_at=timezone.now())
    
    def active(self):
        """Solo objetos no eliminados"""
        return self.filter(deleted=False)
    
    def deleted(self):
        """Solo objetos eliminados"""
        return self.filter(deleted=True)
    
    def all_including_deleted(self):
        """Incluye objetos eliminados"""
        return self


class SoftDeleteManager(models.Manager):
    """Manager que excluye objetos eliminados por defecto"""
    
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(deleted=False)
    
    def all_including_deleted(self):
        """Incluye objetos eliminados"""
        return SoftDeleteQuerySet(self.model, using=self._db)
    
    def deleted_only(self):
        """Solo objetos eliminados"""
        return SoftDeleteQuerySet(self.model, using=self._db).filter(deleted=True)


class SoftDeleteModel(models.Model):
    """Modelo abstracto que proporciona soft delete"""
    deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    
    objects = SoftDeleteManager()
    all_objects = models.Manager()
    
    def delete(self, using=None, keep_parents=False):
        """Marca como eliminado en lugar de borrar"""
        self.deleted = True
        self.deleted_at = timezone.now()
        self.save(using=using)
    
    def hard_delete(self, using=None, keep_parents=False):
        """Elimina físicamente (usar solo si es necesario)"""
        super().delete(using=using, keep_parents=keep_parents)
    
    def restore(self):
        """Restaura un objeto eliminado"""
        self.deleted = False
        self.deleted_at = None
        self.save()
    
    class Meta:
        abstract = True


# Mixin para DeleteViews que usan soft delete
class SoftDeleteMixin:
    """Mixin para que DeleteView use soft delete en lugar de borrado físico"""
    
    def delete(self, request, *args, **kwargs):
        """Reemplaza el delete de Django para usar soft delete"""
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()  # Esto llamará al delete() customizado del modelo
        return super().delete(request, *args, **kwargs)


# Utilidades para filtrar objetos en vistas
class SoftDeleteQuerySetMixin:
    """Mixin para que las vistas genéricas filtren por deleted=False por defecto"""
    
    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(qs.model, 'objects') and hasattr(qs.model.objects, 'active'):
            # El modelo tiene un manager de soft delete, así que ya filtra
            return qs
        return qs.filter(deleted=False)

