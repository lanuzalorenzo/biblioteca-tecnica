# Red en Azure

La red es lo que decide qué se puede alcanzar y qué no. En Azure todo recurso nace dentro de una red privada y desde ahí se expone, o no, al exterior. Entender la red es entender por qué un servicio responde, por qué otro no llega y por qué una base de datos no debería tener dirección pública.

## Privado por defecto

Una red virtual tiene un espacio de direcciones propio y nadie entra desde fuera si no se abre una puerta. Esa es la decisión que hay que tomar primero: qué se publica y con qué intermediario.

## Segmentar no es aislar

Repartir en subredes ordena, pero no separa: dos subredes de la misma red se ven sin permiso adicional. El aislamiento se construye con reglas, y cerrar la salida importa tanto como filtrar la entrada.

## Por qué importa

Una dirección pública puesta para una prueba sobrevive a la prueba. Un grupo de seguridad que solo filtra la entrada deja salir cualquier cosa. Y un punto de conexión privado mal resuelto rompe el servicio sin avisar.
