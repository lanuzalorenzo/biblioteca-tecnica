# Administración básica y trabajo en consola

Un servidor se parece a un edificio en servicio: lo que importa no es cómo se construyó, sino que la calefacción siga funcionando, que nadie entre por donde no debe y que cuando algo se estropea haya un registro de qué pasó. Este módulo trata de eso: de la operación diaria.


## Puesta en marcha

Arrancar un servidor no es encenderlo: es llevarlo a un estado conocido.

- **Objetivos de systemd:** `multi-user.target` para un servidor sin entorno gráfico, `graphical.target` para un puesto. Se fija por defecto y se comprueba.
- **Servicios habilitados frente a activos:** `enable` decide qué arranca solo; `start` solo lo arranca ahora. La confusión entre ambos es la causa más común de «funcionaba ayer».
- **Hora y zona:** un servidor con la hora mal no puede autenticar con Kerberos ni ordenar registros. Se sincroniza por red.
- **Nombre e identidad:** nombre de equipo, dominio o grupo de trabajo y dirección fija o reservada. Cambiarlo después rompe certificados y pertenencias.

## Procesos

Un proceso es un programa en ejecución con su identificador, su usuario, su prioridad y su estado. Administrar es saber:

- Qué consume CPU y memoria (`top`, `htop`), y desde cuándo.
- Qué proceso escucha en un puerto (`ss -tulpn`), que es la pregunta que resuelve «el servicio no arranca porque el puerto está ocupado».
- Qué hace un proceso colgado y cómo terminarlo sin dejar datos a medias: primero `TERM`, `KILL` solo cuando no queda otra.
- Qué demonios hay programados y con qué usuario corren. Un servicio con demasiados privilegios es una puerta abierta con horario.

## Ficheros, búsqueda y filtros

La consola se domina cuando se combinan tres cosas: recorrer, filtrar y encadenar.

- **Recorrer:** `ls`, `cd`, `cp`, `mv`, `rm`, `mkdir`; en Windows, `dir`, `copy`, `move`, `del`, `md`.
- **Buscar:** `find` por nombre, tamaño, fecha o permisos —`find /var -size +1G -mtime -7`—; en Windows, `where` y `Get-ChildItem` con filtros.
- **Filtrar:** `grep` sobre contenido, `cut` y `awk` por columnas, `sort` y `uniq` para contar.
- **Encadenar:** la tubería convierte órdenes simples en una consulta. `ss -tulpn | grep :80` responde en un segundo a una pregunta que por interfaz cuesta minutos.

La diferencia entre un administrador que consulta y uno que adivina está casi siempre aquí.

## Red y recursos compartidos

- Direcciones, rutas y resolución de nombres se comprueban antes de tocar configuración: `ip addr`, `ip route`, `ss`, y una consulta de nombres.
- Los recursos compartidos se publican con permisos explícitos y se prueban desde otro equipo con la cuenta real del usuario.
- **Cuotas de disco:** por usuario o por recurso, para que uno no deje sin espacio al resto. Sin cuota, un registro desbocado o una copia mal hecha llenan la partición y tumban el servicio.

## Registro y comprobación

Lo que el sistema cuenta de sí mismo va a `journalctl` y a `/var/log` en Linux, y al Visor de eventos en Windows. La rutina mínima: revisar errores de servicios críticos, inicios de sesión fallidos y espacio disponible.

Un servidor sin revisión periódica sigue funcionando hasta que deja de hacerlo, y entonces nadie sabe desde cuándo. La comprobación se automatiza: es más fiable un guion que avisa que una costumbre.

## Lo que se comprueba

Que tras reiniciar el equipo quedan en marcha los servicios previstos; que el puerto que debe escuchar escucha y no hay otros abiertos sin motivo; que el usuario de uso diario no tiene privilegios de administración; que las cuotas están activas; y que los registros se conservan y llegan a donde deben.

## Errores que se repiten

- Habilitar servicios «por si acaso» y no revisarlos nunca.
- Trabajar como administrador para todo, incluida la navegación.
- Confundir un servicio activo con un servicio habilitado.
- Publicar un recurso con permisos para todos y llamarlo «temporal».

## Órdenes que responden a las preguntas de guardia

```bash
ss -tulpn                          # qué escucha y qué proceso es
ps aux --sort=-%cpu | head         # quién consume
df -h ; du -sh /var/* | sort -h    # qué llena el disco
find /var -type f -size +500M      # ficheros grandes, con criterio
repquota -a                        # estado de las cuotas por usuario
journalctl -p err -b              # errores desde el último arranque
```

El orden importa: primero se mide, después se toca. Reiniciar un servicio antes de saber qué fallaba borra la evidencia.

Las herramientas gráficas de administración —Webmin y similares— no cambian el modelo: escriben en los mismos ficheros de configuración. Sirven para equipos pequeños y para quien empieza, y estorban cuando hay que reproducir un cambio en veinte servidores. Lo que se decide por interfaz se documenta igual que lo que se decide por consola.

## Fuentes

- Páginas de manual de `systemd`, `ss`, `find` y `journalctl`.
- Documentación de Windows Server sobre servicios, cuotas y registro de eventos.
