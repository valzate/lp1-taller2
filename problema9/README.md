# Problema 9: Sistema Distribuido (Coordinación entre servidores)

**Conceptos clave**:

- Múltiples servidores coordinados
- Balanceador de carga simple
- Replicación de datos
- Tolerancia a fallos básica

**Requerimientos**:

- Registro de servidores backend
- Health checks entre servidores
- Distribución de clientes
- Sincronización de datos

**EJECUCION DEL PROGRAMA**
Hay un solo programa el cual se ejcuta en 4 terminales de la siguiente manera:
 - python3 ptp.py 5001 
 - python3 ptp.py 5002 
 - python3 ptp.py 5003 
 - python3 ptp.py 5004
 Se comunican como servidores distintos conectados entre sí 