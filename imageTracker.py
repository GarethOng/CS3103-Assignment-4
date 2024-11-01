# This script contains the source code that was deployed in AWS Lambda
import base64
import boto3

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('myTable')

# Increments the counter value and sends the user the transparent image
def lambda_handler(event, context):
    db_response = table.update_item(
        Key={'myKey':'zero'}, 
        UpdateExpression='ADD #cnt :val',
        ExpressionAttributeNames={'#cnt': 'count'},
        ExpressionAttributeValues={':val': 1},
        ReturnValues="UPDATED_NEW"
    )
    response = s3.get_object(
            Bucket='amazon-s3-mybucket',
            Key='invisible.png',
        )
    image = response['Body'].read()
    return {
        'headers': { "Content-Type": "image/png" },
        'statusCode': 200,
        'body': base64.b64encode(image).decode('utf-8'),
        'isBase64Encoded': True
    }
