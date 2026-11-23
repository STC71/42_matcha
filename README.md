# 💞 Matcha — Dating web application

[![42](https://img.shields.io/badge/42-Matcha-00babc?style=for-the-badge&logo=42)](https://www.42malaga.com/)
[![Web](https://img.shields.io/badge/Web-HTML%20%7C%20CSS%20%7C%20JavaScript-1572B6?style=for-the-badge&logo=html5&logoColor=white)](https://developer.mozilla.org/)
[![Database](https://img.shields.io/badge/Database-PostgreSQL%20%7C%20MySQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Security](https://img.shields.io/badge/Security-Secure%20by%20design-2E7D32?style=for-the-badge)](https://owasp.org/)

> **Alcance:** desarrollar una aplicación de citas segura, usable y explicable, desde la cuenta y el perfil hasta el match y el chat en tiempo real.

## 📚 Índice

- [Objetivos](#-objetivos)
- [Recorrido funcional](#-recorrido-funcional)
- [Arquitectura](#️-arquitectura-de-referencia)
- [Modelo de datos](#️-modelo-de-datos-inicial)
- [Seguridad](#-seguridad-y-privacidad)
- [Requisitos evaluables](#-matriz-de-requisitos-evaluables)
- [Estructura](#-estructura-del-proyecto)
- [Validación](#-definition-of-done)
- [Recursos](#-recursos)

Matcha es una aplicación web de citas. Su recorrido completo va desde el registro y la construcción del perfil hasta el descubrimiento de personas, el interés mutuo y el chat. El objetivo no es solo mostrar tarjetas bonitas: es diseñar un sistema seguro, usable y explicable que trate datos personales con cuidado.

Una analogía: el perfil es una tarjeta de presentación, el buscador es un escaparate con filtros y el “like” es llamar a una puerta. Solo cuando ambas personas abren la puerta aparece el chat.

## 🎯 Objetivos

- Construir una aplicación web full-stack con una base de datos relacional o orientada a grafos.
- Modelar usuarios, perfiles, preferencias, intereses, matches, bloqueos y mensajes.
- Aplicar validación tanto en cliente como en servidor.
- Diseñar una interfaz responsive compatible con Firefox y Chrome actuales.
- Practicar autenticación, sesiones, privacidad y seguridad de uploads.
- Crear una base de evaluación con al menos 500 perfiles distintos.

El subject permite elegir lenguaje, micro-framework, biblioteca de UI y servidor web. La decisión debe documentarse y respetar la restricción de crear manualmente las consultas; no se debe delegar el modelo de datos completo a un ORM.

## 🧭 Recorrido funcional

```text
Registro → verificación por email → perfil completo
     ↓
Descubrir → filtrar → ver perfil → expresar interés
     ↓
Interés recíproco → match → chat
```

### Funcionalidad obligatoria

- Registro con email, username, nombre, apellido y contraseña protegida.
- Rechazo de contraseñas comunes o de diccionario.
- Verificación de cuenta mediante enlace único.
- Login, logout accesible desde cualquier página y recuperación de contraseña.
- Perfil con género, preferencias sexuales, biografía, intereses y fotografías.
- Búsqueda y filtrado de otros perfiles.
- Interés (“like”) y notificación de visitas/intereses según el subject.
- Chat únicamente cuando existe interés recíproco.
- Bloqueo y gestión de visibilidad.
- Base de datos con un mínimo de 500 perfiles.
- Programación de una consulta/cita y consulta de la lista de próximas citas.

### Comportamiento social y de descubrimiento

- Sugerencias alineadas con la orientación sexual; si no se informa, se considera bisexual por defecto.
- Ranking explicable por proximidad, intereses compartidos y mayor fame rating.
- Búsqueda avanzada por edad, rango de fame, ubicación y una o varias etiquetas.
- Ordenación y filtros por edad, ubicación, fame rating y etiquetas.
- Geolocalización GPS hasta el barrio con consentimiento explícito; alternativa manual de ciudad/barrio y posibilidad de modificarla.
- Fame rating público, consistente y relevante, con fórmula documentada.
- Visitas registradas en el historial.
- Estado online o última conexión visible, sin revelar email ni contraseña.

### Notificaciones, conexión y moderación

- Notificaciones en tiempo real, con un retraso máximo de 10 segundos, para like, visita, mensaje, like recíproco y unlike.
- Indicador de notificaciones y mensajes no leídos desde cualquier página.
- Like/unlike sobre el perfil; no se puede dar like sin foto de perfil.
- Match solo cuando el interés es recíproco; el estado de conexión debe ser visible.
- Reporte de perfiles falsos.
- Bloqueo que elimina al usuario de resultados y sugerencias, detiene notificaciones y deshabilita el chat en ambas direcciones.
- Chat en tiempo real entre usuarios conectados, con retraso máximo de 10 segundos.

Los nombres visibles de acciones deben ser respetuosos y claros; la terminología no debe convertir a las personas en simples objetos de puntuación.

## 🏗️ Arquitectura de referencia

```text
Browser
   │ HTTPS
   ▼
Web server ── Router/controllers ── Services
                                  ├── Auth & sessions
                                  ├── Matching & search
                                  ├── Chat
                                  └── Notifications
                                         │
                                         ▼
                                  Relational database
                                  + protected uploads
```

Una separación útil es mantener la lógica de negocio fuera de las vistas: una regla como “solo se puede chatear después de un match” debe cumplirse en el servidor aunque alguien manipule el JavaScript del navegador.

## 🗃️ Modelo de datos inicial

```text
users ── profiles ── profile_photos
  │          │
  ├── preferences
  ├── interests ── matches
  ├── profile_views
  ├── blocks
  └── conversations ── messages
```

Las relaciones y nombres finales deben adaptarse a la implementación. Las contraseñas se almacenan con un algoritmo de hash moderno; nunca se guardan ni se imprimen en claro.

## 🔐 Seguridad y privacidad

- Consultas parametrizadas para impedir SQL injection.
- Escape contextual de salida y protección contra XSS.
- Tokens CSRF en formularios que cambian estado.
- Cookies `Secure`, `HttpOnly` y `SameSite` cuando el despliegue lo permita.
- Rate limiting en login, recuperación y acciones sensibles.
- Validación de tipo, tamaño, extensión y contenido real de imágenes.
- Nombres de archivo aleatorios y uploads fuera de la ruta ejecutable.
- No exponer stack traces, tokens ni datos personales en errores.
- Autorizar cada operación en servidor, no confiar en IDs enviados por el cliente.
- Política clara de borrado, bloqueo y minimización de datos.

## ✅ Matriz de requisitos evaluables

| Área | Comprobación |
|---|---|
| Arranque | Instalación limpia, servidor sin errores visibles ni crashes 5xx |
| Restricciones | Micro-framework con router/templating, sin ORM, validators ni User Account Manager; BD no NoSQL |
| Datos | `.env` para credenciales y mínimo 500 perfiles sembrados |
| Cuenta | Registro, contraseña no común, email verificable, login, reset y logout global |
| Perfil | Orientación, género, bio, hashtags, hasta 5 imágenes y actualización |
| Descubrimiento | Sugerencias ponderadas, búsqueda avanzada, filtros, ordenación y ubicación |
| Seguridad | Hash de contraseñas, validación de formularios/uploads y consultas sin SQL injection |
| Social | Visitas, fame, likes/unlikes, match, reportes, bloqueo y notificaciones |
| Chat | Solo entre conexiones, tiempo real y avisos de no leídos |
| UX | Firefox/Chrome actuales, móvil y resoluciones pequeñas |

Los errores legítimos deben usar códigos HTTP apropiados (400/401/403/404, etc.) y feedback controlado; ocultar un fallo devolviendo siempre `200 OK` es incorrecto. No se deben incluir librerías de tracking de errores como Sentry o Raven.

## 📁 Estructura prevista

```text
matcha/
├── README.md
├── src/
│   ├── controllers/
│   ├── services/
│   ├── repositories/
│   └── views/
├── public/
│   ├── css/
│   └── js/
├── database/
│   ├── schema.sql
│   └── seed.sql
├── tests/
└── docker-compose.yml
```

La estructura anterior es el contrato inicial de organización: la implementación puede añadir módulos, pero debe conservar una separación clara entre HTTP, negocio, persistencia, vistas y recursos públicos.

El árbol inicial contiene plantillas y puntos de entrada (`.env.example`, Compose y SQL), no una aplicación funcional. `CHANGE_ME` y las imágenes de infraestructura deben resolverse antes de ejecutar el entorno.

## 🚀 Flujo de desarrollo previsto

```bash
# Flujo de desarrollo
cp .env.example .env
docker compose up --build -d
```

Después deben ejecutarse migraciones/seed y verificarse los 500 perfiles. Los secretos y datos de desarrollo deben permanecer fuera del control de versiones.

## ✅ Definition of Done

- Un usuario puede completar el flujo registro → verificación → perfil.
- Las búsquedas respetan filtros, privacidad y paginación.
- El match solo aparece cuando el interés es recíproco.
- El chat rechaza usuarios sin permiso incluso si se manipula la petición.
- Hay 500 perfiles de prueba reproducibles.
- La interfaz funciona en móvil y escritorio.
- Los errores tienen respuesta HTTP apropiada y feedback comprensible.
- Las pruebas cubren autenticación, autorización, uploads, consultas y chat.
- La aplicación no expone secretos ni vulnerabilidades conocidas del subject.

## 📚 Recursos

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [MDN Web Docs](https://developer.mozilla.org/)
- [PostgreSQL documentation](https://www.postgresql.org/docs/)
- [Enunciado de Matcha](./en.subject.pdf)
- [Guía de evaluación](./en_eval.pdf)

---

**Una aplicación de citas profesional no optimiza solo el “match”: protege la autonomía, la privacidad y la seguridad de las personas que la usan.**

## 👤 Autor

**sternero** · 42 Málaga · [GitHub @STC71](https://github.com/STC71)

[⬆️ Volver arriba](#-matcha--dating-web-application)
