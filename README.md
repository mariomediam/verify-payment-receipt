# API de Validación Automática de Recibos de Pago del SATP

Esta API permite cargar un archivo PDF que contiene la imagen de un recibo de pago emitido por el **Servicio de Administración Tributaria del SATP** y extraer automáticamente información clave como el número de recibo, fecha, contribuyente, monto, glosa, entre otros. El objetivo es automatizar el proceso de verificación de recibos de pago, una tarea que antes se realizaba manualmente.

## Características

- **Carga de PDF**: Permite cargar archivos PDF con imágenes de recibos de pago del SATP.
- **Extracción automática de información**: Extrae datos clave como número de recibo, fecha, contribuyente, monto, glosa, etc.
- **Formato JSON**: Los resultados se devuelven en formato JSON para facilitar la integración con otros sistemas.
- **Automatización del proceso de validación**: Implementada en el sistema de **mesa de partes virtual de la Municipalidad** para validar automáticamente la veracidad de los recibos de pago presentados en los expedientes virtuales por los ciudadanos.

## Tecnologías Utilizadas

- **Django**: Framework web usado para construir la API.
- **LangChain**: Usado para la manipulación avanzada del lenguaje natural y para interpretar los datos extraídos de los recibos.
- **OpenAI**: Proporciona la inteligencia artificial que permite interpretar los datos del recibo.

## Cómo Funciona

1. **Subir un archivo PDF**: El usuario carga un archivo PDF que contiene la imagen de un recibo de pago del SATP.
2. **Procesamiento del PDF**: El sistema extrae automáticamente los datos clave del recibo.
4. **Resultado en JSON**: La información extraída del recibo se devuelve en formato JSON para su uso en otros sistemas o procesos.

## Ejemplo de Respuesta JSON

```json
{
    "number": "004651228",
    "payment_date": "05/09/2024",
    "taxpayer_code": "20487840549",
    "taxpayer_name": "MTM TRANSPORTES DE CARGA E.I.R.L.",
    "payment_hour": "10:31:42",
    "amount": 68.44,
    "gloss": "PERM. DE INGRESO PARA EL TRANSP. ES",
    "observation": "AUTORIZACION CARGA Y DESCARGA PLACA M3H-981"
}
```

## Deploy con docker compose
Antes de empezar, [instala Compose](https://docs.docker.com/compose/install/).

```
$ docker compose up -d
```

Después de que se inicie la aplicación, llame a la API `http://localhost:8000/extract-text/` tal como se aprecia en el video anterior 👍

