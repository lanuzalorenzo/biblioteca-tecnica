# Gestión de APIs

API Management resuelve tres problemas antes de que la petición llegue al servicio: identificarla, contarla y comprobar que quien llama es quien dice ser. Las tres cosas se configuran como políticas y se aplican en el gateway, sin tocar el código del backend.

## Gateway, productos y suscripciones

La API se publica en el gateway con una ruta pública. Para consumirla, el cliente se suscribe a un **producto**, que agrupa una o varias APIs y define si hace falta aprobación. Cada suscripción genera dos claves; la cuota y el límite se aplican después con políticas sobre la suscripción, no al crearla.

La clave viaja en la cabecera `Ocp-Apim-Subscription-Key`. Identifica a la suscripción, no a la persona: dos aplicaciones con la misma clave son indistinguibles. Para saber quién llama de verdad hace falta un token de usuario o una identidad de aplicación.

Una clave se revoca regenerando la clave concreta, la primaria o la secundaria; regenerar las dos invalida ambas. Las claves no caducan solas; si se filtran, hay que regenerarlas y avisar al consumidor. Tampoco se usan como único control: son un identificador de facturación y de cuota, no una prueba de identidad.

## Políticas

Una política es un XML con cuatro bloques: `inbound`, `backend`, `outbound` y `on-error`. El gateway ejecuta los bloques en ese orden. `base` aplica la política heredada del ámbito superior, que puede ser el producto, la API o la operación.

```xml
<policies>
  <inbound>
    <base />
    <rate-limit-by-key calls="60" renewal-period="60"
        counter-key="@(context.Subscription.Id)" />
    <quota-by-key calls="10000" renewal-period="86400"
        counter-key="@(context.Subscription.Id)" />
  </inbound>
  <backend>
    <base />
  </backend>
  <outbound>
    <base />
    <set-header name="Server" exists-action="delete" />
  </outbound>
  <on-error>
    <base />
  </on-error>
</policies>
```

`rate-limit-by-key` corta ráfagas: 60 llamadas por minuto y por suscripción. `quota-by-key` limita el total del periodo: 10.000 llamadas al día. El primero protege al backend de un pico; el segundo, de un consumo que se sale del contrato.

La cuota y el límite se pueden contar por suscripción, por usuario o por dirección IP. La elección importa: contar por IP castiga a quien comparte salida a internet, y contar por usuario deja fuera a las llamadas sin usuario. Lo habitual es una clave por consumidor y el contador sobre la suscripción.

## Validar el token

La suscripción identifica al consumidor, pero no prueba que su token sea válido. Para eso está `validate-jwt`, que comprueba firma, emisor, audiencia y caducidad contra el documento de configuración de OpenID Connect:

```xml
<validate-jwt header-name="Authorization"
    failed-validation-httpcode="401"
    require-scheme="Bearer">
  <openid-config
      url="https://login.microsoftonline.com/<tenant-id>/v2.0/.well-known/openid-configuration" />
  <audiences>
    <audience>api://<app-id></audience>
  </audiences>
  <issuers>
    <issuer>https://login.microsoftonline.com/<tenant-id>/v2.0</issuer>
  </issuers>
</validate-jwt>
```

El bloque va en `inbound`, antes de la llamada al backend. `failed-validation-httpcode` decide qué recibe el cliente cuando el token no vale; el `401` es lo esperado. La audiencia debe ser la de la API, no la del cliente: si se acepta cualquier `api://`, un token emitido para otro servicio sirve aquí.

La configuración de OpenID se cachea. Si el tenant rota las claves de firma, el gateway las refresca solo; no hay que reiniciar nada.

## Cabeceras y errores

El gateway añade y quita cabeceras. `set-header` sirve para borrar las que anuncian el servidor o la versión del backend, y para inyectar un identificador de correlación que después aparece en los registros de los dos lados.

En `on-error` se decide qué se devuelve cuando algo falla. Un error del backend no se copia tal cual: se transforma en una respuesta propia, con un código estable y sin detalles internos. El cliente recibe `502` o `503`; el detalle queda en el registro del gateway.

## Versiones y revisiones

Una **revisión** es un cambio que se prueba antes de publicarlo; no cambia la ruta. Una **versión** es una ruta nueva, por ejemplo `/v2`, que convive con la anterior. La revisión sirve para corregir sin romper; la versión, para cambiar el contrato y dar tiempo a migrar.

El backend puede seguir en la misma dirección. Lo que cambia es la ruta pública y la política que se aplica. Esa separación es la que permite retirar una versión sin tocar el servicio.

## Lo que la capa no resuelve

API Management no arregla una API sin autenticación: si la clave de suscripción es el único control, cualquiera que la obtenga entra. Tampoco sustituye a una red privada ni a un WAF. Para eso están el punto de conexión privado, la integración con red virtual y, delante, Front Door o Application Gateway.

La política se escribe una vez y se audita como código. Un cambio de cuota o de validación de token es un cambio de configuración, no un despliegue, y debe pasar por el mismo control de versiones que el backend.
