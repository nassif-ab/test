# Documentación del Sistema de Recomendación

## Introducción

Este documento explica el funcionamiento del sistema de recomendación implementado en la aplicación de blog. El sistema utiliza técnicas de filtrado colaborativo y análisis de contenido para proporcionar recomendaciones personalizadas a los usuarios basadas en sus interacciones previas.

## Arquitectura del Sistema

El sistema de recomendación está compuesto por los siguientes componentes:

1. **Clase RecommendationSystem**: Implementada en `RecommendationSystem.py`, esta clase contiene toda la lógica para generar recomendaciones.
2. **Endpoints de API**: Implementados en `routers/posts.py`, estos endpoints permiten a la aplicación frontend solicitar recomendaciones.
3. **Script de entrenamiento**: `train_recommendation_system.py` permite entrenar y probar el sistema con los datos existentes.

## Algoritmo de Recomendación

### 1. Recomendaciones Personalizadas para Usuarios

El algoritmo utiliza un enfoque híbrido que combina:

#### a) Filtrado Colaborativo con SVD (Descomposición en Valores Singulares)

```python
def _build_user_item_matrix(self):
    # Construye una matriz de interacciones usuario-item
    # Filas: usuarios, Columnas: posts
    # Valores: ponderación de interacciones (likes = 2, visitas = 1)
```

```python
def _apply_svd(self, matrix, n_components = 10):
    # Aplica SVD para reducir dimensionalidad y descubrir patrones latentes
    svd = TruncatedSVD(n_components=n_components)
    matrix_reduced = svd.fit_transform(matrix)
    reconstructed_matrix = matrix_reduced @ svd.components_
```

#### b) Análisis de Preferencias por Categoría

```python
# Contar las interacciones por categoría
category_weights = defaultdict(int)
for post in interacted_posts:
    # Dar más peso a los likes (x3) que a las visitas (x1)
    like_weight = 3 if post.id in [like.post_id for like in user_likes] else 0
    visit_weight = 1 if post.id in [visit.post_id for visit in user_visits] else 0
    category_weights[post.categorie] += (like_weight + visit_weight)
```

#### c) Puntuación Combinada

```python
# Calcular puntuación combinada (SVD + categoría)
combined_score = svd_score + category_bonus
```

### 2. Recomendaciones de Posts Similares

Para encontrar posts similares a uno específico, el sistema:

1. Primero busca posts de la misma categoría
2. Si no hay suficientes, utiliza similitud de coseno basada en categorías

```python
# Filtrar posts por categoría si está disponible
if post.categorie:
    category_posts = [p for p in all_posts if p.categorie == post.categorie and p.id != post_id]
```

## Mecanismo de Caché

Para mejorar el rendimiento, el sistema implementa un mecanismo de caché:

```python
# Cache para resultados de recomendaciones
self.user_based_recommendations_cache = {}
self.content_based_recommendations_cache = {}
self.similar_posts_cache = {}
# Cuándo se actualizó el caché por última vez
self.last_cache_update = datetime.datetime.now()
# Tiempo de expiración del caché (12 horas)
self.cache_expiry = datetime.timedelta(hours=12)
```

## Cómo Activar las Recomendaciones

### 1. Actualización Automática de Recomendaciones

El sistema ha sido modificado para actualizar las recomendaciones automáticamente con cada nueva interacción del usuario:

- Cuando un usuario da "me gusta" a una publicación, sus recomendaciones se actualizan inmediatamente
- Cuando un usuario visita una publicación, sus recomendaciones se actualizan inmediatamente
- Al visitar una publicación, también se actualiza la lista de publicaciones similares para esa publicación

Esto significa que las recomendaciones mejoran continuamente con cada interacción, sin necesidad de entrenamiento manual.

### 2. Entrenamiento Manual (Opcional)

También puedes ejecutar el entrenamiento manual para actualizar todas las recomendaciones de una vez:

```bash
cd backend
.\venv\Scripts\activate
python train_recommendation_system.py
```

Este script:
- Invalida el caché de todas las recomendaciones
- Analiza todas las interacciones existentes en la base de datos
- Genera nuevas recomendaciones para todos los usuarios y publicaciones

### 2. Uso en la Aplicación

#### a) Recomendaciones para Usuarios

Las recomendaciones personalizadas se obtienen a través del endpoint:

```
GET /api/posts/user/{user_id}/recommendations
```

Este endpoint devuelve una lista de posts recomendados para el usuario especificado.

#### b) Posts Similares

Para obtener posts similares a uno específico, se utiliza el endpoint:

```
GET /api/posts/{post_id}/similar
```

Este endpoint devuelve una lista de posts similares al post especificado.

## Mejores Prácticas

1. **Entrenar regularmente**: Ejecuta `train_recommendation_system.py` periódicamente para mantener las recomendaciones actualizadas.

2. **Fomentar interacciones**: Cuantas más interacciones (likes y visitas) haya, mejores serán las recomendaciones.

3. **Categorizar correctamente**: Asegúrate de que todos los posts tengan una categoría asignada para mejorar la precisión de las recomendaciones.

## Solución de Problemas

### Recomendaciones no relevantes

Si las recomendaciones no parecen relevantes:

1. Verifica que el usuario tenga suficientes interacciones (likes y visitas)
2. Ejecuta `train_recommendation_system.py` para actualizar el sistema
3. Asegúrate de que los posts tengan categorías correctamente asignadas

### Error "Matriz demasiado pequeña para SVD"

Este mensaje aparece cuando no hay suficientes datos para aplicar SVD. En este caso, el sistema utilizará métodos alternativos:

1. Recomendaciones basadas en categorías preferidas
2. Posts populares como fallback

## Conclusión

El sistema de recomendación está diseñado para mejorar con el tiempo a medida que los usuarios interactúan más con el blog. Las recomendaciones se vuelven más precisas y personalizadas con cada interacción adicional.
