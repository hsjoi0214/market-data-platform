FROM public.ecr.aws/lambda/python:3.12

# Install dependencies first (better layer caching)
COPY requirements.txt ${LAMBDA_TASK_ROOT}/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the application code needed for Lambda
COPY pipelines ${LAMBDA_TASK_ROOT}/pipelines
COPY schemas ${LAMBDA_TASK_ROOT}/schemas

# If you rely on any top-level config files, copy them explicitly
# COPY pyproject.toml ${LAMBDA_TASK_ROOT}/pyproject.toml

CMD ["pipelines.streaming.ingest_lambda.lambda_handler.lambda_handler"]