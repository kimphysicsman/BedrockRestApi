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

import qna_flows_rest_api
from dispatch.utils import generate_response

class TestQnAFlowsRestApi(unittest.TestCase):
    """Test cases for the QnA Flows REST API Lambda handler."""

    def setUp(self):
        """Set up test fixtures."""
        # Sample API Gateway event
        self.event = {
            'body': json.dumps({
                'sessionId': 'test-session-id',
                'message': 'Hello, world!',
                'metadata': {'filter': 'test-filter'}
            }),
            'requestContext': {
                'authorizer': {
                    'principalId': 'test-user'
                }
            }
        }
        
        # Sample Lambda context
        self.context = MagicMock()

    @patch('qna_flows_rest_api.BedrockFlowsRouter')
    def test_lambda_handler_success(self, mock_router_class):
        """Test successful Lambda handler execution."""
        # Mock router instance
        mock_router = MagicMock()
        mock_router.session_id = 'test-session-id'
        mock_router_class.return_value = mock_router
        
        # Mock chat_with_flow response
        mock_router.chat_with_flow.return_value = {
            'message': 'This is a test response',
            'citations': [{'url': 'https://example.com', 'title': 'Example'}]
        }
        
        # Call the handler
        response = qna_flows_rest_api.lambda_handler(self.event, self.context)
        
        # Verify response
        expected_response = generate_response(200, {
            'sessionId': 'test-session-id',
            'message': 'This is a test response',
            'citations': [{'url': 'https://example.com', 'title': 'Example'}]
        })
        self.assertEqual(response, expected_response)
        
        # Verify router initialization
        mock_router_class.assert_called_once_with(
            'test-session-id',
            {'principalId': 'test-user'},
            {'filter': 'test-filter'}
        )
        
        # Verify chat_with_flow call
        mock_router.chat_with_flow.assert_called_once_with('Hello, world!')

    @patch('qna_flows_rest_api.BedrockFlowsRouter')
    def test_lambda_handler_no_citations(self, mock_router_class):
        """Test Lambda handler with response without citations."""
        # Mock router instance
        mock_router = MagicMock()
        mock_router.session_id = 'test-session-id'
        mock_router_class.return_value = mock_router
        
        # Mock chat_with_flow response without citations
        mock_router.chat_with_flow.return_value = {
            'message': 'This is a test response without citations'
        }
        
        # Call the handler
        response = qna_flows_rest_api.lambda_handler(self.event, self.context)
        
        # Verify response
        expected_response = generate_response(200, {
            'sessionId': 'test-session-id',
            'message': 'This is a test response without citations'
        })
        self.assertEqual(response, expected_response)

    def test_lambda_handler_no_body(self):
        """Test Lambda handler with no body."""
        event = {'body': None}
        response = qna_flows_rest_api.lambda_handler(event, self.context)
        expected_response = generate_response(400, {'Message': 'No body found'})
        self.assertEqual(response, expected_response)

    def test_lambda_handler_no_message(self):
        """Test Lambda handler with no message."""
        event = {
            'body': json.dumps({'sessionId': 'test-session-id'}),
            'requestContext': {'authorizer': {'principalId': 'test-user'}}
        }
        response = qna_flows_rest_api.lambda_handler(event, self.context)
        expected_response = generate_response(400, {'message': 'Message not provided'})
        self.assertEqual(response, expected_response)

    @patch('qna_flows_rest_api.BedrockFlowsRouter')
    def test_lambda_handler_router_exception(self, mock_router_class):
        """Test Lambda handler with router initialization exception."""
        # Mock router initialization exception
        mock_router_class.side_effect = Exception('Router initialization error')
        
        # Call the handler
        response = qna_flows_rest_api.lambda_handler(self.event, self.context)
        
        # Verify response
        self.assertEqual(response['statusCode'], 500)
        response_body = json.loads(response['body'])
        self.assertEqual(response_body['message'], 'Router initialization error')

    @patch('qna_flows_rest_api.BedrockFlowsRouter')
    def test_lambda_handler_chat_exception(self, mock_router_class):
        """Test Lambda handler with chat_with_flow exception."""
        # Mock router instance
        mock_router = MagicMock()
        mock_router.session_id = 'test-session-id'
        mock_router_class.return_value = mock_router
        
        # Mock chat_with_flow exception
        mock_router.chat_with_flow.side_effect = Exception('Chat error')
        
        # Call the handler
        response = qna_flows_rest_api.lambda_handler(self.event, self.context)
        
        # Verify response
        self.assertEqual(response['statusCode'], 500)
        response_body = json.loads(response['body'])
        self.assertEqual(response_body['message'], 'Chat error')


if __name__ == '__main__':
    unittest.main()