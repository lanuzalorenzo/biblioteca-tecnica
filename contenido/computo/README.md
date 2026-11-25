# Cómputo en Azure

Cómputo es donde corre el código: la máquina, el plan, el contenedor o la función. Elegir mal no rompe el sistema el primer día; se nota al escalar, al facturar o al intentar ponerle una red privada. La decisión se toma por tres criterios: cuánto control necesitas, cuánto quieres administrar y cuánto puede esperar una petición.

## Control y administración

Una máquina virtual da control total y cobra en trabajo de parcheo. Un servicio de plataforma renuncia a parte del control y se queda con el sistema operativo. La pregunta no es cuál es mejor, sino cuánto de eso quieres mantener tú.

## El coste sigue al modelo

Un plan encendido cuesta aunque no reciba tráfico; una función apagada no cuesta. La diferencia obliga a mirar la forma del tráfico antes que el precio por hora.

## Por qué importa

Un servicio publicado sin identidad administrada acaba con una contraseña en una variable de entorno. Una función que se queda sin tiempo se arregla cambiando de plan, no de código.
