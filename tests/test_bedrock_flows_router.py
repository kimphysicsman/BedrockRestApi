# Copyright Amazon.com and its affiliates; all rights reserved.
# SPDX-License-Identifier: LicenseRef-.amazon.com.-AmznSL-1.0
# Licensed under the Amazon Software License  https://aws.amazon.com/asl/

import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import json

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dispatch.bedrock_flows_router import BedrockFlowsRouter

class TestBedrockFlowsRouter(unittest.TestCase):
    """Test cases for the BedrockFlowsRouter class."""

    @patch('boto3.client')
    def setUp(self, mock_boto3_client):
        """Set up test fixtures."""
        self.mock_bedrock_runtime = MagicMock()
        mock_boto3_client.return_value = self.mock_bedrock_runtime
        
        # Set environment variable for testing
        os.environ['BEDROCK_FLOW_ID'] = 'test-flow-id'
        
        # Create router instance
        self.session_id = 'test-session-id'
        self.session_attributes = {'principalId': 'test-user'}
        self.metadata = {'filter': 'test-filter'}
        self.router = BedrockFlowsRouter(
            session_id=self.session_id,
            session_attributes=self.session_attributes,
            metadata=self.metadata
        )

    def test_init(self):
        """Test initialization of the router."""
        self.assertEqual(self.router.flow_id, 'test-flow-id')
        self.assertEqual(self.router.session_id, self.session_id)
        self.assertEqual(self.router.session_attributes, self.session_attributes)
        self.assertEqual(self.router.metadata, self.metadata)

    def test_chat_with_flow_success(self):
        """Test successful flow invocation."""
        # Mock response from Bedrock Flow
        mock_response = {
            'output': {
                'content': {
                    'messageContent': 'This is a test response',
                    'citations': [{'url': 'https://example.com', 'title': 'Example'}]
                }
            }
        }
        self.mock_bedrock_runtime.invoke_flow.return_value = mock_response
        
        # Call the method
        result = self.router.chat_with_flow('Hello, world!')
        
        # Verify the result
        self.assertEqual(result['message'], 'This is a test response')
        self.assertEqual(result['citations'], [{'url': 'https://example.com', 'title': 'Example'}])
        
        # Verify the call to invoke_flow
        self.mock_bedrock_runtime.invoke_flow.assert_called_once()
        call_args = self.mock_bedrock_runtime.invoke_flow.call_args[1]
        self.assertEqual(call_args['flowId'], 'test-flow-id')
        
        # Verify input content
        input_content = call_args['input']['content']
        self.assertEqual(input_content['messageContent'], 'Hello, world!')
        self.assertEqual(input_content['sessionId'], self.session_id)
        self.assertEqual(input_content['sessionAttributes'], self.session_attributes)
        self.assertEqual(input_content['metadata'], self.metadata)

    def test_chat_with_flow_no_citations(self):
        """Test flow invocation with no citations in response."""
        # Mock response from Bedrock Flow without citations
        mock_response = {
            'output': {
                'content': {
                    'messageContent': 'This is a test response without citations'
                }
            }
        }
        self.mock_bedrock_runtime.invoke_flow.return_value = mock_response
        
        # Call the method
        result = self.router.chat_with_flow('Hello, world!')
        
        # Verify the result
        self.assertEqual(result['message'], 'This is a test response without citations')
        self.assertNotIn('citations', result)

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_flow_id(self):
        """Test behavior when flow ID is not set."""
        router = BedrockFlowsRouter()
        with self.assertRaises(ValueError):
            router.chat_with_flow('Hello, world!')

    def test_exception_handling(self):
        """Test exception handling during flow invocation."""
        # Mock an exception
        self.mock_bedrock_runtime.invoke_flow.side_effect = Exception('Test error')
        
        # Verify exception is propagated
        with self.assertRaises(Exception) as context:
            self.router.chat_with_flow('Hello, world!')
        
        self.assertEqual(str(context.exception), 'Test error')


if __name__ == '__main__':
    unittest.main()