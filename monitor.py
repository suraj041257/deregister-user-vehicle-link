from datetime import datetime
import boto3

OCTOPUS_API_COUNT_METRIC_NAMESPACE = 'Octopus Api Calls'

OCTOPUS_API_COUNT_METRIC_NAME = 'octopus_apis'

cloudwatch = boto3.client('cloudwatch')

def put_metric_data_set(namespace, name, timestamp, unit, data_set, dimensions = []):
    """
    Sends a set of data to CloudWatch for a metric. All of the data in the set
    have the same timestamp and unit.
    :param namespace: The namespace of the metric.
    :param name: The name of the metric.
    :param timestamp: The UTC timestamp for the metric.
    :param unit: The unit of the metric.
    :param data_set: The set of data to send. This set is a dictionary that
                        contains a list of values and a list of corresponding counts.
                        The value and count lists must be the same length.
    """
    print(name, data_set['values'][0], unit, namespace, dimensions)
    response = cloudwatch.put_metric_data(
        
        MetricData=[{
            'MetricName': name,
            'Timestamp': timestamp,
            'Value': data_set['values'][0],
            'Unit': unit,
            'Dimensions': dimensions 
            }],
        Namespace=namespace,
        )
    print('cloudwatch_response', response)

def monitor_api_calls(api, user_id):

    metric_namespace = OCTOPUS_API_COUNT_METRIC_NAMESPACE
    metric_name = OCTOPUS_API_COUNT_METRIC_NAME

    print(f"Putting data into metric {metric_namespace}.{metric_name}.")
    
    put_metric_data_set(
        namespace=metric_namespace, 
        name=metric_name, 
        timestamp=datetime.utcnow(), 
        unit='Count',
        data_set={
            'values': [1],
        },
        dimensions=[
            {
                'Name': 'user_id',
                'Value': user_id
            },
            {
                'Name': 'api_address',
                'Value': api
            }
        ]
    )