# This script contains the source code that was deployed in AWS Lambda
import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('myTable')

# Sends the user the counter value
def lambda_handler(event, context):
    db_response = table.get_item(
        Key={'myKey':'zero'}
    )

    return {
        'statusCode': 200,
        'body': db_response['Item']['count']
    }
