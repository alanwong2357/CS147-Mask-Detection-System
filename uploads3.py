import logging
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from datetime import datetime
from simple_camera import take_picture

class s3Upload:
    def __init__(self):
        self.bucket = '$iots3'
        self.s3 = boto3.client('s3',
                aws_access_key_id='',
                aws_secret_access_key= '11VhuJ++j25W2MNAjIT0NJ',
                region_name=''
        )
        self.photo = 'capture.jpg'

    def upload_picture(self):
        """ 
        takes picture and uploads it to an s3 bucket
        """
        take_picture()
        # photo = 'capture'
        filename = self.photo + '.jpg'
        # print(filename)
        # upload to s3 bucket
        with open(self.photo, "rb") as f:
            self.s3.upload_fileobj(f, self.bucket, self.photo)


    def detect_labels(self):

        client=boto3.client('rekognition',
            aws_access_key_id='',
            aws_secret_access_key= '',
            region_name='us-east-1'
            )
        response = client.detect_protective_equipment(
            Image={
                'S3Object':{'Bucket':self.bucket,'Name':self.photo}
            }
        )
        return response

    def check_mask(self,label):
        for i in label['Persons'][0]['BodyParts']:
            # print(i)
            # print("\n")
            if(i['Name'] == 'FACE'):
                if(len(i['EquipmentDetections']) > 0):
                    print(i['EquipmentDetections'])
                    for equipment in i['EquipmentDetections']:
                        if(equipment['Type'] == 'FACE_COVER'):
                            if(equipment['CoversBodyPart']['Value']) == True:
                                # print('wearing mask')
                                return 'Wearing Mask'
                            else: 
                                # print('not wearing mask properly')
                                return 'Mask Not Worn Properly'
                else:
                    print('not wearing mask')
                    return 'Not Wearing Mask'

    def update_db(self,state):
        # value can be 'Wearing Mask', 'Mask Not Worn Properly', 'Not Wearing Mask'
        dynamodb = boto3.resource('dynamodb',
                aws_access_key_id='',
                aws_secret_access_key= '',
                region_name='us-west-1'
        )
        table = dynamodb.Table('mask-db')
        now = datetime.now()
        date = now.date()
        timestamp = now.strftime("%H:%M:%S")
        response = table.put_item(
            Item = {
                'Date': str(date),
                'Time': str(timestamp),
                'State': state 
            }
        )
        print('Added item: ', date, timestamp, state, 'to db')
        return response
    
    def get_today_stats(self, date):
        dynamodb = boto3.resource('dynamodb',
                aws_access_key_id='',
                aws_secret_access_key= '',
                region_name='us-west-1'
        )
        table = dynamodb.Table('mask-db')
        response = table.query(
            KeyConditionExpression=
                Key('Date').eq(date)
        )
        # print(response['Items'])
        mask_not_worn_properly = 0
        no_mask = 0
        mask_worn = 0
        for i in response['Items']:
            if(i['State'] == 'Mask Not Worn Properly'):
                mask_not_worn_properly += 1
            elif(i['State'] == 'Not Wearing Mask'):
                no_mask += 1
            elif(i['State'] == 'Wearing Mask'):
                mask_worn += 1
        return 'Mask Stats on ' + date + ':\n' + \
                '   People Wearing Masks: ' + str(mask_worn) + '\n' + \
                '   People Not Wearing Masks Properly: ' + str(mask_not_worn_properly) + '\n' + \
                '   People Not Wearing Masks: ' + str(no_mask) + '\n'
        # return response['Items']
        




if __name__ == '__main__':
    s3upload = s3Upload()
#    photo='person_not_wearing_properly'
    photo = 'capture'
    bucket='$iots3'
    s3 = boto3.client('s3',
            aws_access_key_id='',
            aws_secret_access_key= '',
            region_name='us-east-1'
    )

    # upload image to s3
    filename = photo + '.jpg'
    print(filename)
    with open(filename, "rb") as f:
       s3.upload_fileobj(f, bucket, photo)

    # mask recognition
    recog = s3upload.detect_labels()
    print(recog)
    state = s3upload.check_mask(recog)

    # # updating db
    s3upload.update_db(state)

    print(s3upload.get_today_stats('2021-06-01'))
