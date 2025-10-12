# Configuración de Email para el Sistema

## Opciones de Configuración de Email

El sistema necesita enviar emails para:
- Enviar contraseñas temporales a nuevos usuarios
- Recuperación de contraseñas olvidadas

Tienes varias opciones para configurar el envío de emails:

## Opción 1: Gmail (Desarrollo/Producción Pequeña)

### Paso 1: Configurar Gmail

1. Ve a tu cuenta de Google: https://myaccount.google.com/
2. Ve a "Seguridad"
3. Activa la "Verificación en 2 pasos"
4. Después de activarla, busca "Contraseñas de aplicaciones"
5. Genera una contraseña de aplicación para "Correo"
6. Copia la contraseña generada (16 caracteres)

### Paso 2: Configurar .env

Agrega estas líneas a tu archivo `.env`:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tucorreo@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
DEFAULT_FROM_EMAIL=Sistema Peticiones <tucorreo@gmail.com>
```

**Nota**: Reemplaza `xxxx xxxx xxxx xxxx` con la contraseña de aplicación generada.

## Opción 2: Outlook/Hotmail

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tucorreo@outlook.com
EMAIL_HOST_PASSWORD=tu_contraseña
DEFAULT_FROM_EMAIL=Sistema Peticiones <tucorreo@outlook.com>
```

## Opción 3: Servidor SMTP Institucional

Si tu entidad tiene un servidor de correo propio:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.tuinstitucion.gov.co
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=sistema@tuinstitucion.gov.co
EMAIL_HOST_PASSWORD=contraseña_del_correo
DEFAULT_FROM_EMAIL=Sistema de Peticiones <sistema@tuinstitucion.gov.co>
```

**Nota**: Consulta con el departamento de IT de tu institución para obtener:
- Servidor SMTP
- Puerto
- Si usa TLS o SSL
- Credenciales de la cuenta de correo

## Opción 4: Consola (Solo Desarrollo)

Para desarrollo, puedes hacer que los emails se muestren en la consola en lugar de enviarse:

```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

Con esta configuración:
- Los emails NO se envían realmente
- Se muestran en la consola donde ejecutas `python manage.py runserver`
- Útil para pruebas sin necesidad de configurar un servidor SMTP real

## Opción 5: SendGrid (Producción Profesional)

SendGrid es un servicio profesional de envío de emails con plan gratuito (100 emails/día):

### Paso 1: Crear cuenta en SendGrid

1. Ve a https://sendgrid.com/
2. Crea una cuenta gratuita
3. Verifica tu email
4. Crea una API Key en Settings > API Keys

### Paso 2: Instalar dependencia

```bash
pip install sendgrid
```

### Paso 3: Configurar .env

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=tu_api_key_de_sendgrid
DEFAULT_FROM_EMAIL=noreply@tudominio.com
```

## Opción 6: Mailgun (Producción)

Mailgun ofrece 5,000 emails gratis por mes:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=postmaster@tu-dominio.mailgun.org
EMAIL_HOST_PASSWORD=tu_contraseña_mailgun
DEFAULT_FROM_EMAIL=noreply@tudominio.com
```

## Verificar Configuración

Para verificar que el email funciona correctamente, puedes usar el shell de Django:

```bash
python manage.py shell
```

Luego ejecuta:

```python
from django.core.mail import send_mail

send_mail(
    'Prueba de Email',
    'Este es un email de prueba del sistema.',
    'noreply@tudominio.com',
    ['tu_email@ejemplo.com'],
    fail_silently=False,
)
```

Si todo está bien configurado, recibirás el email de prueba.

## Solución de Problemas

### Error: "SMTPAuthenticationError"

**Causa**: Credenciales incorrectas o autenticación no permitida.

**Solución**:
- Verifica que el usuario y contraseña sean correctos
- Para Gmail, asegúrate de usar una contraseña de aplicación
- Verifica que la cuenta permita acceso de aplicaciones menos seguras

### Error: "SMTPConnectError"

**Causa**: No se puede conectar al servidor SMTP.

**Solución**:
- Verifica que el HOST y PORT sean correctos
- Verifica tu conexión a internet
- Verifica que no haya firewall bloqueando el puerto

### Error: "SMTPServerDisconnected"

**Causa**: El servidor cerró la conexión.

**Solución**:
- Verifica que EMAIL_USE_TLS esté configurado correctamente
- Algunos servidores usan SSL en lugar de TLS (puerto 465)

### Los emails van a SPAM

**Solución**:
- Usa un dominio verificado
- Configura registros SPF y DKIM en tu dominio
- Usa un servicio profesional como SendGrid o Mailgun
- Evita palabras spam en el asunto y contenido

## Configuración Recomendada por Entorno

### Desarrollo Local
```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Staging/Testing
```env
# Gmail con cuenta de prueba
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=pruebas@gmail.com
EMAIL_HOST_PASSWORD=contraseña_aplicacion
```

### Producción
```env
# Servidor institucional o servicio profesional
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.institucion.gov.co
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=sistema@institucion.gov.co
EMAIL_HOST_PASSWORD=contraseña_segura
DEFAULT_FROM_EMAIL=Sistema de Peticiones <noreply@institucion.gov.co>
```

## Plantillas de Email

El sistema envía dos tipos de emails:

### 1. Bienvenida (Nuevo Usuario)

```
Asunto: Bienvenido al Sistema de Gestión de Peticiones

Hola [Nombre],

Bienvenido al Sistema de Gestión de Derechos de Petición.

Tus credenciales de acceso son:
- Usuario (Cédula): [Cédula]
- Contraseña temporal: [Contraseña]

Por seguridad, deberás cambiar tu contraseña en el primer inicio de sesión.

Puedes acceder al sistema en: [URL]

Saludos,
Equipo de Sistemas
```

### 2. Recuperación de Contraseña

```
Asunto: Recuperación de Contraseña

Hola [Nombre],

Has solicitado recuperar tu contraseña.

Para crear una nueva contraseña, haz clic en el siguiente enlace:
[URL de recuperación]

Si no solicitaste este cambio, ignora este correo.

El enlace expirará en 24 horas.

Saludos,
Equipo de Sistemas
```

## Personalización de Emails

Si deseas personalizar los emails, edita el archivo:
`peticiones/auth_views.py`

Busca las funciones:
- `registro_usuario()` - Email de bienvenida
- `recuperar_contrasena()` - Email de recuperación

---

**Última actualización**: 2025-01-11
