from aws_cdk import (
    Stack,
    aws_s3 as s3,
    CfnOutput
)
from constructs import Construct

class StorageStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        """
        Using the same bucket name cause I want to stay within the
        limits of aws free tier lol :) ..
        """
        self.bucket = s3.Bucket.from_bucket_name(
            self, 
            "VirtualLennyData",    
            "virtual-lenny-bucket"  
        )

        CfnOutput(self, "DataBucketName", value=self.bucket.bucket_name)