# Requisitos del Proyecto: Ruleta de la Vida

## Introducción

"Ruleta de la Vida" es una aplicación web en Flask que permite a los usuarios autoevaluar ocho áreas fundamentales de su vida (salud, relaciones, carrera, finanzas, desarrollo personal, ocio, espiritualidad y entorno) mediante cuestionarios interactivos. La plataforma visualiza los resultados a través de gráficos intuitivos como el radar, facilitando la identificación de fortalezas y áreas de mejora.

El sistema segmenta datos por variables demográficas (sexo, edad, estado civil) para análisis de patrones, e implementa diferentes roles de usuario: administradores con acceso a estadísticas avanzadas y usuarios regulares enfocados en su progreso personal


## Requisitos Funcionales

| ID | Categoría | Requisito | Descripción | Prioridad |
|----|-----------|-----------|-------------|-----------|
| RF01 | Gestión de Usuarios | Registro | Los usuarios crean cuentas con nombre, correo, contraseña y teléfono. | Alta |
| RF02 | Gestión de Usuarios | Autenticación | Sistema de login seguro con opción de recuperación de contraseña. | Alta |
| RF03 | Gestión de Usuarios | Perfiles | Los usuarios pueden ver y editar su información personal. | Media |
| RF04 | Gestión de Usuarios | Roles | Distinción entre usuarios normales y administradores. | Alta |
| RF05 | Evaluación | Cuestionario | Formulario con preguntas sobre 8 áreas de la vida. | Alta |
| RF06 | Evaluación | Calificación | Escala del 1 al 10 para cada pregunta. | Alta |
| RF07 | Evaluación | Guardado | Las respuestas se almacenan asociadas al usuario. | Alta |
| RF08 | Evaluación | Periodicidad | Opción para realizar evaluaciones regulares. | Media |
| RF09 | Visualización | Resumen personal | Vista general de las calificaciones del usuario. | Alta |
| RF10 | Visualización | Gráfico de radar | Visualización de puntuaciones por categoría. | Alta |
| RF11 | Visualización | Historial | Acceso a evaluaciones anteriores y progreso. | Media |
| RF12 | Visualización | Recomendaciones | Sugerencias basadas en las puntuaciones. | Baja |
| RF13 | Administración | Dashboard | Estadísticas generales de todos los usuarios. | Alta |
| RF14 | Administración | Gestión de usuarios | Lista y control de cuentas de usuario. | Alta |
| RF15 | Administración | Análisis avanzado | Filtros por categoría, edad, sexo y otros criterios. | Media |
| RF16 | Administración | Exportación | Descarga de datos en formato Excel. | Media |
| RF17 | Análisis | Tendencias | Visualización de cambios en el tiempo. | Media |
| RF18 | Análisis | Correlaciones | Análisis de relaciones entre categorías. | Media |
| RF19 | Análisis | Segmentación | Análisis por grupos demográficos. | Media |

## Requisitos No Funcionales

| ID | Categoría | Requisito | Descripción | Métrica |
|----|-----------|-----------|-------------|---------|
| RNF01 | Seguridad | Almacenamiento seguro de contraseñas | Uso de hash para las contraseñas. | Implementación de generate_password_hash |
| RNF02 | Seguridad | Control de acceso | Protección de rutas según el rol del usuario. | Uso de decoradores login_required y admin_required |
| RNF03 | Seguridad | Sesiones seguras | Gestión de sesiones con clave secreta. | Implementación de clave secreta en Flask |
| RNF04 | Usabilidad | Interfaz responsiva | Diseño adaptable a diferentes dispositivos. | Funcionalidad completa en móviles, tablets y escritorio |
| RNF05 | Usabilidad | Feedback visual | Notificaciones para acciones del usuario. | Implementación de flash messages |
| RNF06 | Usabilidad | Controles intuitivos | Uso de sliders para calificaciones con feedback visual. | Visualización del valor seleccionado en tiempo real |
| RNF07 | Rendimiento | Carga eficiente de datos | Consultas SQLite3 optimizadas. | Tiempo de respuesta < 1 segundo para consultas comunes |
| RNF08 | Rendimiento | Generación de gráficos | Uso de matplotlib para generar visualizaciones. | Tiempo de generación < 2 segundos |
| RNF09 | Rendimiento | Procesamiento asíncrono | Manejo de solicitudes AJAX para actualizar datos sin recargar la página. | Actualización de interfaz < 1 segundo |
| RNF10 | Mantenibilidad | Estructura modular | Separación clara de funcionalidades. | Organización en módulos independientes |
| RNF11 | Mantenibilidad | Código comentado | Documentación en el código para facilitar mantenimiento. | Comentarios en funciones principales y secciones complejas |
| RNF12 | Mantenibilidad | Manejo de errores | Captura y gestión de excepciones. | Implementación de bloques try-except en operaciones críticas |
| RNF13 | Escalabilidad | Arquitectura extensible | Posibilidad de añadir nuevas categorías o preguntas. | Diseño modular que permita extensiones sin modificar código existente |
| RNF14 | Escalabilidad | Base de datos relacion