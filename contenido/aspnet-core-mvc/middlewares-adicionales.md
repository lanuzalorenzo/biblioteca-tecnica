# Middlewares adicionales

Dos middlewares del *framework* resuelven tareas que antes se delegaban al servidor frontal: comprimir la respuesta y reescribir la URL. Tenerlos en la aplicación permite que el comportamiento viaje con el código y no dependa de la configuración de IIS, Apache o Nginx.

## Compresión de respuestas

Comprimir reduce el ancho de banda y acelera la descarga, a cambio de CPU. El middleware `ResponseCompression` aplica GZip o Brotli a los tipos que se le indiquen y negocia con el navegador mediante la cabecera `Accept-Encoding`. Se registra así:

```csharp
builder.Services.AddResponseCompression(options =>
{
    options.Providers.Add<BrotliCompressionProvider>();
    options.Providers.Add<GzipCompressionProvider>();
    options.MimeTypes = ResponseCompressionDefaults.MimeTypes;
    options.EnableForHttps = true;
});

builder.Services.Configure<GzipCompressionProviderOptions>(options =>
{
    options.Level = CompressionLevel.Fastest;
});
```

`Providers` contiene los algoritmos disponibles. En cada petición el middleware recorre la colección y elige el primero que entienda el `Accept-Encoding` del cliente. `MimeTypes` limita la compresión a texto, CSS, JavaScript, HTML y JSON; comprimir un JPEG o un ZIP no ahorra nada y gasta CPU.

`EnableForHttps` está desactivado por defecto porque la compresión sobre TLS abre la puerta a ataques de tipo BREACH cuando la respuesta mezcla secretos y datos controlados por el atacante. Se activa solo si no hay secretos en el cuerpo.

El middleware se añade al pipeline antes de los componentes que generan la respuesta:

```csharp
app.UseResponseCompression();

app.MapGet("/texto", () => new string('x', 1_000_000));
```

Sin compresión, el millón de caracteres viaja entero. Con compresión, el mismo contenido ocupa unos pocos kilobytes. El resultado se comprueba en la pestaña de red del navegador o con `curl --compressed`: la respuesta trae `Content-Encoding: gzip` o `br`.

## Reescritura de URL

`RewriteMiddleware` modifica la ruta de la petición o devuelve una redirección antes de que llegue al resto del pipeline. Sirve para conservar URLs antiguas, forzar HTTPS o traducir reglas que antes vivían en el servidor. Se configura con `UseRewriter` y un objeto `RewriteOptions`:

```csharp
var options = new RewriteOptions()
    .AddRedirectToHttps(StatusCodes.Status302Found, 5001);

app.UseRewriter(options);
```

`AddRedirectToHttps` responde con una redirección; `AddRewrite` cambia la ruta internamente sin que el cliente lo note. El ejemplo convierte `/app/1/2` en `/application/2/1`:

```csharp
var options = new RewriteOptions()
    .AddRewrite(@"app/(\d+)/(\d+)", "application/$2/$1", skipRemainingRules: false);

app.UseRewriter(options);
```

`skipRemainingRules` decide si se siguen evaluando las reglas posteriores cuando esta coincide. Si se activa, el orden de las reglas pasa a ser parte de la lógica.

También se pueden importar reglas escritas para IIS o para el módulo `mod_rewrite` de Apache:

```csharp
var options = new RewriteOptions()
    .AddIISUrlRewrite(app.Environment.ContentRootFileProvider, "IISUrlConfig.xml")
    .AddApacheModRewrite(app.Environment.ContentRootFileProvider, "ApacheRewriteConfig.txt");

app.UseRewriter(options);
```

La reescritura ocurre dentro de la aplicación, así que el servidor frontal sigue viendo la URL original. Si hay un proxy delante, conviene decidir en un solo sitio quién reescribe: dos capas con reglas parecidas producen redirecciones circulares difíciles de diagnosticar.

## Dónde colocarlos

Compresión y reescritura van al principio del pipeline, antes de los componentes que generan la respuesta. La compresión debe envolver a todo lo que escriba un cuerpo; la reescritura, cambiar la ruta antes de que el enrutado la lea. Si se colocan al final, el cuerpo ya se ha enviado y la ruta ya se ha resuelto.

Ninguno de los dos sustituye a la configuración del servidor frontal. En un despliegue con Nginx o un CDN, la compresión puede hacerse allí con menos coste para la aplicación, y la redirección a HTTPS en el balanceador. Tenerla también en el código es útil para desarrollo y para entornos sin proxy, pero duplicarla sin criterio complica el diagnóstico.
