from django.shortcuts import render
from rest_framework.views import APIView  
from rest_framework.generics import CreateAPIView
from django.http import JsonResponse  
from langchain_core.pydantic_v1 import BaseModel, Field

import os
import json
import base64

# from langchain.chains import create_structured_output_runnable
from langchain_openai import ChatOpenAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pdf2image import convert_from_path
from langchain_core.messages import HumanMessage


from .serializers import UploadFilePDFSerializer

# Constantes
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
PATH_DOCS = os.environ.get('PATH_DOCS')
VALID_EXTENSIONS = ["pdf"]
PROMPT_USER_TEMPLATE = '''Eres un asistente que solo habla en JSON. No genere salida que no esté en JSON correctamente formateada.
Se te va a proporcionar una imagen de un recibo de pago  y debes retornar en formato JSON los siguientes campos:

- number: <str> Número del recibo. Ejemplo 004651223
- payment_date: <date> La fecha del recibo en formato dd/mm/yyyy. Ejemplo 05/09/2024
- taxpayer_code: <str> El código del contribuyente. Ejemplo 20487840549
- taxpayer_name: <str> El nombre del contribuyente. Ejemplo MTM TRANSPORTES DE CARGAR EIRL
- payment_hour: <time> La hora del recibo en formato hh:mm:ss. Ejemplo 14:30:00
- amount: <float> El monto del recibo. Ejemplo 68.44
- gloss: <str> Un resumen del recibo. Ejemplo PERM. DE INGRESO PARA EL TRANSP. ES
- observation: <str> Una observación del recibo. Ejemplo AUTORIZACION CARGA Y DESCARGA PLACA  T4I-899


Ejemplo: Se te pasa la siguiente imagen

*******************************************************************************
SATP PIURA
SERVICIO DE ADMINISTRACIÓN TRIBUTARIA

                SERVICIO DE ADMINISTRACIÓN TRIBUTARIA DE PIURA
                            R.U.C. 20441554436

    Calle Arequipa Nº 1052 Piura - Teléfono 285400 / http://www.satp.gob.pe

PAGINA          : 1 DE 1
RECIBO No.      : 004651223
FECHA DE PAGO   : 05/09/2024
CAJERO          : jgonzalesn
CONTRIBUYENTE   : (20487840549) MTM TRANSPORTES DE CARGAR EIRL

HORA            : 14:30:00
UNID/PLACA/LF   :

CONV/PAPEL      : PERM. DE INGRESO PARA EL TRANSP. ES

J66-2024 001/001          00.00
AUTORIZACION CARGA Y DESCARGA PLACA  T4I-899




                                                                68.44

*******************************************************************************

Debes retornar lo siguiente en formato JSON:
{{
    "number": "004651223",
    "payment_date": "05/09/2024",
    "taxpayer_code": "20487840549",
    "taxpayer_name": "MTM TRANSPORTES DE CARGAR EIRL",
    "payment_hour": "14:30:00",
    "amount": 68.44,
    "gloss": "PERM. DE INGRESO PARA EL TRANSP. ES",
    "observation": "AUTORIZACION CARGA Y DESCARGA PLACA  T4I-899"    
}}

{context}
'''

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

def get_images_from_pdf(file_name):
    images = convert_from_path(file_name)
    return images

def is_valid_extension(extension):
    return extension in VALID_EXTENSIONS

def get_file_extension(file_name):
    return file_name.split(".")[-1]

def encode_image(image_path):
    # Función para codificar la imagen en base64
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

class ReceiptFormat(BaseModel):
    """Retorna los principales datos del recibo de pago"""

    number: str = Field(..., description="Número del recibo.")
    payment_date: str = Field(..., description="Fecha del recibo.")
    taxpayer_code: str = Field(..., description="Código del contribuyente.")
    taxpayer_name: str = Field(..., description="Nombre del contribuyente.")
    payment_hour: str = Field(..., description="Hora del recibo.")
    amount: float = Field(..., description="Monto del recibo.")
    gloss: str = Field(..., description="Un resumen del recibo.")
    observation: str = Field(..., description="Una observación del recibo.")    

# Vistas
class HomeView(APIView):  
    def get(self, request, format=None):
        return JsonResponse({"message": 'HOLA MUNDO DESDE DJANGO Y DOCKER', "content": 'Por Mario Medina'}) 

class ExtractTextView(CreateAPIView):  
    def post(self, request, format=None):
        try:            
            file_name = "doc_origin.pdf"
            location = f"{PATH_DOCS}/"

            dataArchivo = request.FILES.copy()
            dataArchivo["location"] = location
            dataArchivo["file_name"] = file_name

            request_file_name = dataArchivo["archivo"].name
            extension = get_file_extension(request_file_name)
            
            if not is_valid_extension(extension):
                return JsonResponse({"message": 'Tipo de archivo no permitido', "content": ''})

            self.serializer_class = UploadFilePDFSerializer
            data = self.serializer_class(data=dataArchivo)

            if data.is_valid():
                pdf_name_save = data.save()
                pdf_file_path = f"{location}{pdf_name_save}"               
                
                images = get_images_from_pdf(pdf_file_path)                
                image_name_save = "payment.jpg"
                image_file_path = f"{location}{image_name_save}"
                images[0].save(image_file_path, 'jpeg')
                
                base64_image = encode_image(image_file_path) # Codifica la imagen en base64

                # elinina archivos
                os.remove(pdf_file_path)
                os.remove(image_file_path)

                # Configura y usa LangChain con el modelo de OpenAI
                llm = ChatOpenAI(model="gpt-4o-mini", max_tokens=256)                
                prompt = ChatPromptTemplate.from_messages(
                    [
                        ("system", PROMPT_USER_TEMPLATE),
                        HumanMessage(
                            content=[
                                {
                                    "type": "text", 
                                    "text": "Esta es la imagen del recibo de pago",
                                },
                                {
                                    "type": "image_url",
                                    "image_url":  {
                                            "url": f"data:image/jpeg;base64,{base64_image}",
                                            "detail": "auto",
                                        },
                                },
                            ]
                        )
                    ]
                )
                                            
                parser = JsonOutputParser(pydantic_object=ReceiptFormat)                
                chain = create_stuff_documents_chain(llm, prompt, output_parser=parser)                
                result = chain.invoke(({"context": ""})  )                              
                response = JsonResponse({"message": '', "content": result})
                response['Content-Type'] = 'application/json; charset=utf-8'
                return response
                
            
        except Exception as e:
            print(e)
            return JsonResponse({"message": str(e.args), "content": 'Error en el servidor'})