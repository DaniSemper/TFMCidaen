import json
import boto3
import io
import numpy as np
import PIL.Image as Image
import matplotlib.pyplot as plt
import cv2
import uuid
import os


import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from urllib.parse import unquote

IMAGE_WIDTH = 224
IMAGE_HEIGHT = 224

IMAGE_SHAPE = (IMAGE_WIDTH, IMAGE_HEIGHT)
model =  load_model('model/')

S3_BUCKET = 'tfm-dsemper'
s3_client = boto3.client('s3', region_name='us-east-1')

s3 = boto3.resource('s3')
dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')
dybamodb_table = dynamodb_resource.Table("predictions-covid")


def CLAHE(rgb):
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    lab[:, :, 0] = clahe.apply(lab[:, :, 0])
    return cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
    

def downloadFromS3(strBucket, s3_path, local_path):
    s3_client.download_file(strBucket, s3_path, local_path)
    

def lambda_handler(event, context):
  url = unquote(event['pathParameters']['url'])
  

  bucket_name = S3_BUCKET
  key = 'input/'+url
  downloadFromS3(S3_BUCKET,key,"/tmp/"+key.split('/')[1])  
  ##Cargamos y aplicamos el filtro antes del analisis
  img= np.array([cv2.cvtColor(cv2.imread("/tmp/"+key.split('/')[1]), cv2.COLOR_BGR2RGB)])
  img = np.expand_dims(img, axis=0)
  #img = image.load_img("/tmp/"+key.split('/')[1], target_size=(224, 224))
  lahe = CLAHE(img[0][0]) 
  im = Image.fromarray(lahe)
  im.save("/tmp/"+key.split('/')[1])  
  img = image.load_img("/tmp/"+key.split('/')[1], target_size=(224, 224))
  img = np.array(img)/255.0
  img = np.expand_dims(img, axis=0)
  prediction = model.predict(img)
  out = ('{:.2%} COVID,  {:.2%} NORMAL,  {:.2%} VIRAL '.format(prediction[0][0],prediction[0][1],prediction[0][2]))
  
  with dybamodb_table.batch_writer() as batch:
    nuevo_item = {             
                 "photoid": str(key.split('/')[1]),            
                 "COVID": '{:.2%}'.format(prediction[0][0]),            
                 "NORMAL":  '{:.2%}'.format(prediction[0][1]),
                 "VIRAL": '{:.2%}'.format(prediction[0][2])                 
            } 
    try:
            response = batch.put_item(Item=nuevo_item)  
    except Exception as e:
                print(f'Problema durante la escritura: {e}') 
                      
  
  
  return {
         'headers': {
            'Access-Control-Allow-Origin': '*'
        },
        'statusCode': 200,
        'body': json.dumps({'COVID': '{:.2%}'.format(prediction[0][0]),
                            'NORMAL':  '{:.2%}'.format(prediction[0][1]),
                            'VIRAL':'{:.2%}'.format(prediction[0][2]),
                            'URL':url})
    }

