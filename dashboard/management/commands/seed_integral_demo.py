from decimal import Decimal
from itertools import cycle
from random import Random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from clientes.models import Cliente
from inventario.models import MateriaPrima, MovimientoMateriaPrima
from produccion.models import OrdenProduccion, ProduccionDiaria
from productos.models import Categoria, IngredienteReceta, Producto, ProductoMovimiento, Receta
from proveedores.models import Proveedor
from usuario.models import Usuario
from ventas.models import DetalleVenta, Venta


class Command(BaseCommand):
    help = 'Genera usuarios y datos demo coherentes para todo el sistema de forma idempotente.'

    def add_arguments(self, parser):
        parser.add_argument('--role-users', type=int, default=15)
        parser.add_argument('--records', type=int, default=20)

    @transaction.atomic
    def handle(self, *args, **options):
        role_users = max(options['role_users'], 15)
        records = max(options['records'], 20)
        rng = Random(20260618)
        now = timezone.now()

        summary = {
            'usuarios_admin': 0,
            'usuarios_cliente': 0,
            'usuarios_logistica': 0,
            'clientes': 0,
            'proveedores': 0,
            'materias_primas': 0,
            'productos': 0,
            'ventas': 0,
            'detalles_venta': 0,
            'ordenes_produccion': 0,
            'producciones_diarias': 0,
            'movimientos_mp': 0,
            'movimientos_producto': 0,
        }

        admin_users = self._create_role_users('admin', role_users, summary)
        client_users = self._create_role_users('cliente', role_users, summary)
        logistics_users = self._create_role_users('logistica', role_users, summary)

        categories = self._create_categories(records)
        providers = self._create_providers(records, summary)
        clients = self._create_clients(records, client_users, summary)
        materias = self._create_materias(records, providers, summary, rng)
        products = self._create_products(records, categories, materias, summary, rng)
        self._create_sales(records, products, clients, admin_users, summary, now, rng)
        self._create_production(records, products, logistics_users, summary, now, rng)

        self.stdout.write(self.style.SUCCESS('Carga demo integral completada.'))
        for key, value in summary.items():
            self.stdout.write(f'{key}: {value}')

    def _create_role_users(self, role, count, summary):
        created_users = []
        role_label = {
            'admin': 'Administrador',
            'cliente': 'Cliente',
            'logistica': 'Logistica',
        }[role]
        first_names = ['Ana', 'Luis', 'Marta', 'Carlos', 'Sofia', 'Diego', 'Paula', 'Andres', 'Valeria', 'Mateo', 'Lucia', 'Jorge', 'Elena', 'Daniel', 'Camila']
        last_names = ['Gomez', 'Ruiz', 'Torres', 'Morales', 'Castro', 'Herrera', 'Lopez', 'Rojas', 'Silva', 'Ortega', 'Mendoza', 'Delgado', 'Vargas', 'Jimenez', 'Pena']

        for index in range(1, count + 1):
            username = f'{role}_{index:02d}'
            email = f'{username}@gafra.local'
            password = f'Gafra{role_label}2026!{index:02d}'
            first_name = first_names[(index - 1) % len(first_names)]
            last_name = last_names[(index - 1) % len(last_names)]

            user, _ = User.objects.get_or_create(username=username, defaults={'email': email})
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.is_active = True
            user.is_staff = role in {'admin', 'logistica'}
            user.is_superuser = role == 'admin'
            user.set_password(password)
            user.save()

            Usuario.objects.update_or_create(
                user=user,
                defaults={
                    'rol': role,
                    'telefono': f'300100{index:04d}',
                    'activo': True,
                },
            )
            created_users.append(user)

        summary[f'usuarios_{role}'] = count
        return created_users

    def _create_categories(self, records):
        base_categories = [
            ('Linea Hogar', 'Productos para el hogar'),
            ('Movilidad', 'Productos de transporte y movilidad'),
            ('Descanso', 'Elementos de descanso y confort'),
            ('Accesorios', 'Accesorios complementarios'),
            ('Seguridad', 'Elementos de seguridad'),
        ]
        categories = []
        for index in range(records):
            name, description = base_categories[index % len(base_categories)]
            category, _ = Categoria.objects.get_or_create(
                nombre=f'{name} {index + 1:02d}',
                defaults={'descripcion': description},
            )
            categories.append(category)
        return categories

    def _create_providers(self, records, summary):
        cities = ['Bogota', 'Medellin', 'Cali', 'Barranquilla', 'Bucaramanga']
        providers = []
        for index in range(1, records + 1):
            provider, _ = Proveedor.objects.update_or_create(
                nombre=f'Proveedor Demo {index:02d}',
                defaults={
                    'razon_social': f'Proveedor Demo {index:02d} SAS',
                    'rfc': f'DEMO{index:09d}'[:13],
                    'contacto': f'Contacto {index:02d}',
                    'telefono': f'310200{index:04d}',
                    'email': f'proveedor{index:02d}@demo.local',
                    'direccion': f'Calle {index} # {index + 10}-45',
                    'ciudad': cities[(index - 1) % len(cities)],
                    'estado': 'Cundinamarca',
                    'pais': 'Colombia',
                    'codigo_postal': f'11{index:03d}',
                    'tipo': 'Nacional' if index % 4 else 'Extranjero',
                    'sitio_web': f'https://proveedor{index:02d}.demo.local',
                    'activo': True,
                },
            )
            providers.append(provider)
        summary['proveedores'] = len(providers)
        return providers

    def _create_clients(self, records, client_users, summary):
        clients = []
        for index in range(1, records + 1):
            linked_user = client_users[(index - 1) % len(client_users)]
            if index <= len(client_users):
                email = linked_user.email
                name = linked_user.get_full_name() or linked_user.username
            else:
                email = f'cliente_demo_extra_{index:02d}@gafra.local'
                name = f'Cliente Extra {index:02d}'
            client, _ = Cliente.objects.update_or_create(
                email=email,
                defaults={
                    'nombre': name,
                    'documento': f'CC{index:08d}',
                    'direccion': f'Avenida {index} # {index + 2}-20',
                    'telefono': f'320300{index:04d}',
                },
            )
            clients.append(client)
        summary['clientes'] = len(clients)
        return clients

    def _create_materias(self, records, providers, summary, rng):
        unit_cycle = cycle(['kg', 'g', 'l', 'ml', 'pz', 'caja'])
        materias = []
        for index in range(1, records + 1):
            provider = providers[(index - 1) % len(providers)]
            materia, _ = MateriaPrima.objects.update_or_create(
                nombre=f'Materia Prima Demo {index:02d}',
                defaults={
                    'descripcion': f'Insumo demo {index:02d} para procesos integrales',
                    'marca': f'Marca {index:02d}',
                    'proveedor': provider,
                    'precio_unitario': Decimal(1000 + index * 75),
                    'unidad_medida': next(unit_cycle),
                    'stock_actual': Decimal(150 + index * 5),
                    'stock_minimo': Decimal(20 + index),
                    'ubicacion': f'Bodega-{(index - 1) % 5 + 1}',
                    'observaciones': 'Generado automaticamente',
                    'activo': True,
                },
            )
            materias.append(materia)
            movement, _ = MovimientoMateriaPrima.objects.get_or_create(
                materia_prima=materia,
                tipo='entrada',
                cantidad=Decimal(10 + index),
                motivo='Carga demo inicial',
                defaults={'precio_unitario': materia.precio_unitario},
            )
            if movement.precio_unitario is None:
                movement.precio_unitario = materia.precio_unitario
                movement.save(update_fields=['precio_unitario'])
        summary['materias_primas'] = len(materias)
        summary['movimientos_mp'] = MovimientoMateriaPrima.objects.filter(motivo='Carga demo inicial').count()
        return materias

    def _create_products(self, records, categories, materias, summary, rng):
        products = []
        for index in range(1, records + 1):
            category = categories[(index - 1) % len(categories)]
            product, _ = Producto.objects.update_or_create(
                nombre=f'Producto Demo {index:02d}',
                defaults={
                    'descripcion': f'Producto demo {index:02d} asociado a {category.nombre}',
                    'categoria': category,
                    'precio_costo': Decimal(25000 + index * 500),
                    'precio_venta': Decimal(35000 + index * 900),
                    'stock_actual': 20 + index,
                    'activo': True,
                },
            )
            recipe, _ = Receta.objects.update_or_create(
                producto=product,
                defaults={
                    'descripcion': f'Receta demo para {product.nombre}',
                    'tiempo_produccion': 45 + index,
                    'activo': True,
                },
            )
            ingredient_choices = [materias[(index - 1) % len(materias)], materias[(index + 3) % len(materias)]]
            used_ids = set()
            for position, materia in enumerate(ingredient_choices, start=1):
                if materia.id in used_ids:
                    continue
                used_ids.add(materia.id)
                IngredienteReceta.objects.update_or_create(
                    receta=recipe,
                    materia_prima=materia,
                    defaults={'cantidad_requerida': Decimal('1.50') + Decimal(position) / Decimal('2')},
                )
            ProductoMovimiento.objects.get_or_create(
                producto=product,
                tipo='creacion',
                motivo='Carga demo inicial',
                defaults={
                    'cantidad': Decimal(product.stock_actual),
                    'usuario': 'seed_integral_demo',
                },
            )
            products.append(product)
        summary['productos'] = len(products)
        summary['movimientos_producto'] = ProductoMovimiento.objects.filter(motivo='Carga demo inicial').count()
        return products

    def _create_sales(self, records, products, clients, admin_users, summary, now, rng):
        seller = admin_users[0]
        summary['detalles_venta'] = 0
        for index in range(1, records + 1):
            client = clients[(index - 1) % len(clients)]
            venta, _ = Venta.objects.update_or_create(
                numero_venta=f'DEMO-V-{index:04d}',
                defaults={
                    'vendedor': seller,
                    'cliente': client,
                    'estado': 'completada' if index % 3 else 'pendiente',
                    'impuesto': Decimal('0.00'),
                    'descuento': Decimal('0.00'),
                    'total': Decimal('0.00'),
                    'observaciones': f'Venta demo {index:02d}',
                    'fecha_completado': now if index % 3 else None,
                },
            )
            venta.detalles.all().delete()
            total = Decimal('0.00')
            for offset in range(2):
                product = products[(index + offset) % len(products)]
                quantity = index % 4 + 1 + offset
                subtotal = product.precio_venta * quantity
                DetalleVenta.objects.create(
                    venta=venta,
                    producto=product,
                    cantidad=quantity,
                    precio_unitario=product.precio_venta,
                    subtotal=subtotal,
                )
                total += subtotal
                summary['detalles_venta'] += 1
            venta.total = total
            venta.save(update_fields=['total', 'estado', 'fecha_completado', 'observaciones', 'cliente', 'vendedor'])
        summary['ventas'] = Venta.objects.filter(numero_venta__startswith='DEMO-V-').count()

    def _create_production(self, records, products, logistics_users, summary, now, rng):
        responsible = logistics_users[0]
        states = ['pendiente', 'en_progreso', 'completada', 'cancelada']
        for index in range(1, records + 1):
            product = products[(index - 1) % len(products)]
            recipe = product.receta
            state = states[(index - 1) % len(states)]
            orden, _ = OrdenProduccion.objects.update_or_create(
                producto=product,
                notas=f'DEMO-OP-{index:04d}',
                defaults={
                    'receta': recipe,
                    'cantidad_a_producir': 5 + index,
                    'estado': state,
                    'fecha_inicio': now if state in {'en_progreso', 'completada'} else None,
                    'fecha_fin': now if state == 'completada' else None,
                    'responsable': responsible,
                },
            )
            ProduccionDiaria.objects.update_or_create(
                orden_produccion=orden,
                fecha=now.date(),
                defaults={
                    'cantidad_producida': orden.cantidad_a_producir if state == 'completada' else max(0, orden.cantidad_a_producir - 2),
                    'tiempo_trabajado': 60 + index,
                    'observaciones': 'Produccion demo completada' if state == 'completada' else 'Seguimiento demo de orden',
                    'responsable': responsible,
                },
            )
        summary['ordenes_produccion'] = OrdenProduccion.objects.filter(notas__startswith='DEMO-OP-').count()
        summary['producciones_diarias'] = ProduccionDiaria.objects.filter(orden_produccion__notas__startswith='DEMO-OP-').count()
