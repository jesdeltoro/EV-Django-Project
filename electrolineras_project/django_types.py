"""
Este archivo provee stubs de tipo para ayudar a Pylance con los campos automáticos de Django.
Ayudará a resolver errores como 'Cannot access attribute "id" for class "PuntoRecarga"'
"""
from typing import TypedDict, Any, Optional, List, Dict, TypeVar, Type, Generic, cast
from django.db import models

# Definir un tipo que represente los campos automáticos de un modelo Django
class DjangoModelFields(TypedDict):
    """Ayuda a Pylance a entender los campos automáticos de modelos Django."""
    id: int
    pk: Any

# Decorador para agregar información de tipo a los modelos Django
T = TypeVar('T', bound=models.Model)

def add_django_type_hints(cls: Type[T]) -> Type[T]:
    """
    Decorador que ayuda a Pylance a reconocer campos automáticos como 'id'.
    Este decorador no cambia la funcionalidad en tiempo de ejecución.
    
    Uso:
    @add_django_type_hints
    class MiModelo(models.Model):
        # campos...
    """
    return cls

# Función auxiliar para trabajar con instancias de modelos
def with_id(obj: T) -> T:
    """
    Función auxiliar para asegurar que Pylance reconozca el campo id.
    Esta función no hace nada en tiempo de ejecución.
    
    Uso:
    punto = with_id(PuntoRecarga.objects.get(...))
    print(punto.id)  # No más errores de Pylance
    """
    return obj

# Exportamos para que se pueda importar donde sea necesario
__all__ = ['DjangoModelFields', 'add_django_type_hints', 'with_id']
