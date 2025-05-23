# Copyright Amazon.com and its affiliates; all rights reserved.
# SPDX-License-Identifier: LicenseRef-.amazon.com.-AmznSL-1.0
# Licensed under the Amazon Software License  https://aws.amazon.com/asl/

import json
from dispatch.bedrock_flows_router import BedrockFlowsRouter
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.logging import correlation_paths
from dispatch.utils import generate_response

logger = Logger(use_rfc3339=True)


@logger.inject_lambda_context(log_event=True, correlation_id_path=correlation_paths.API_GATEWAY_REST)
def lambda_handler(event: dict, context: LambdaContext):

    # Validate request is not empty
    request = json.loads(event['body']) if event['body'] else {}
    if not request:
        return generate_response(400, { 'Message' : 'No body found'})

    # Validate message is passed in the request
    session_id: str = request.get('sessionId', None)
    message: str = request.get('message', None)
    if not message:
        return generate_response(400, { 'message' : 'Message not provided'})

    # Collect optional session attributes to pass to Amazon Bedrock Flows
    session_attributes = {}
    session_attributes['principalId'] = event['requestContext'].get('authorizer', {}).get('principalId', "not passed")

    # Collect documents metadata filter
    metadata: dict = request.get('metadata', {})

    logger.info(f'Session ID: {session_id if session_id is not None else "None"}')
    logger.info(f'Session attributes: {session_attributes if session_attributes else "None"}')
    logger.info(f'Message: {message if message is not None else "None"}')
    logger.info(f'Metadata filter: {metadata if metadata else "None"}')

    logger.info(f'Instantiating BedrockFlowsRouter')
    try:
        bedrock_flows_router = BedrockFlowsRouter(session_id, session_attributes, metadata)
    except Exception as e:
        logger.error(f'Error instantiating BedrockFlowsRouter: {e}')
        return generate_response(500, {"sessionId": session_id,
                                       "message" : str(e)})

    logger.info(f'Sending message to BedrockFlowsRouter to get flow response')
    try:
        flow_response = bedrock_flows_router.chat_with_flow(message)
    except Exception as e:
        logger.error(f'Error sending message to BedrockFlowsRouter: {e}')
        return generate_response(500, {"sessionId": bedrock_flows_router.session_id,
                                       "message" : str(e)})
    logger.info(f'Flow response: {flow_response}')

    client_response = {}
    if 'message' in flow_response and 'citations' in flow_response:
        logger.info(f'Returning response to client (message and citations)')
        client_response = generate_response(200, {
            "sessionId": bedrock_flows_router.session_id,
            "message": flow_response['message'],
            "citations": flow_response['citations']
        })
    
    elif 'message' in flow_response and 'citations' not in flow_response:
        logger.info(f'Returning response to client (message only)')
        client_response = generate_response(200, {
            "sessionId": bedrock_flows_router.session_id,
            "message": flow_response['message'],
        })
    else:
        logger.info(f'Returning response to client (no message or citations)')
        client_response = generate_response(500, {
            "sessionId": bedrock_flows_router.session_id,
            "message": "No message or citations found in flow response"
        })
    
    return client_response