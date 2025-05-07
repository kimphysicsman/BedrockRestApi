# Copyright Amazon.com and its affiliates; all rights reserved.
# SPDX-License-Identifier: LicenseRef-.amazon.com.-AmznSL-1.0
# Licensed under the Amazon Software License  https://aws.amazon.com/asl/

import boto3
import uuid
import os
from aws_lambda_powertools import Logger

logger = Logger(use_rfc3339=True)

class BedrockFlowsRouter:
    """
    A class to handle communication with Amazon Bedrock Flows.
    """
    
    def __init__(self, session_id=None, session_attributes=None, metadata=None):
        """
        Initialize the BedrockFlowsRouter with session information.
        
        Args:
            session_id (str, optional): The session ID for the conversation. If None, a new UUID will be generated.
            session_attributes (dict, optional): Additional session attributes to pass to the flow.
            metadata (dict, optional): Metadata for document filtering or other purposes.
        """
        # Initialize Bedrock client
        self.bedrock_runtime = boto3.client('bedrock-runtime')
        
        # Get flow ID from environment variable
        self.flow_id = os.environ.get('BEDROCK_FLOW_ID')
        if not self.flow_id:
            logger.warning("BEDROCK_FLOW_ID environment variable not set")
            
        # Set session ID
        self.session_id = session_id if session_id else str(uuid.uuid4())
        
        # Store session attributes and metadata
        self.session_attributes = session_attributes if session_attributes else {}
        self.metadata = metadata if metadata else {}
        
        logger.info(f"Initialized BedrockFlowsRouter with flow ID: {self.flow_id}")
        
    def chat_with_flow(self, message):
        """
        Send a message to the Bedrock Flow and get the response.
        
        Args:
            message (str): The user message to send to the flow.
            
        Returns:
            dict: The response from the flow containing message and optional citations.
        """
        if not self.flow_id:
            raise ValueError("Flow ID is not set. Please set the BEDROCK_FLOW_ID environment variable.")
        
        try:
            # Prepare the input for the flow
            flow_input = {
                "messageContent": message,
                "sessionId": self.session_id
            }
            
            # Add session attributes if available
            if self.session_attributes:
                flow_input["sessionAttributes"] = self.session_attributes
                
            # Add metadata if available
            if self.metadata:
                flow_input["metadata"] = self.metadata
            
            logger.info(f"Sending message to flow: {self.flow_id}")
            
            # Invoke the flow
            response = self.bedrock_runtime.invoke_flow(
                flowId=self.flow_id,
                input={
                    'content': flow_input
                }
            )
            
            # Process the response
            response_body = response.get('output', {}).get('content', {})
            logger.info(f"Received response from flow: {response_body}")
            
            # Extract message and citations if available
            result = {}
            
            if 'messageContent' in response_body:
                result['message'] = response_body['messageContent']
                
            if 'citations' in response_body:
                result['citations'] = response_body['citations']
                
            return result
            
        except Exception as e:
            logger.error(f"Error invoking Bedrock Flow: {str(e)}")
            raise