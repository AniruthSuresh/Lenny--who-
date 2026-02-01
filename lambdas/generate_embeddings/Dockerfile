FROM public.ecr.aws/lambda/python:3.11

# Needed for torch / tokenizers
RUN yum install -y gcc gcc-c++ make && yum clean all

COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

COPY handler.py .

CMD ["handler.lambda_handler"]
