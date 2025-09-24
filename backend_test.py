#!/usr/bin/env python3
"""
Backend Testing Suite for Brigada Paulista Website
Tests authentication, forum API, and image upload functionality
"""

import requests
import json
import base64
import io
from PIL import Image
import time

# Configuration
BASE_URL = "https://movimento-paulista.preview.emergentagent.com/api"
TEST_USERNAME = "paulista_revolucionario"
TEST_PASSWORD = "saopaulo1932"
TEST_USERNAME_2 = "bandeirante_livre"
TEST_PASSWORD_2 = "independencia2025"

class BrigadaPaulistaAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        self.auth_token_2 = None
        self.test_thread_id = None
        self.test_results = {
            "authentication": {},
            "forum": {},
            "image_upload": {},
            "errors": []
        }
    
    def log_result(self, category, test_name, success, message, response_data=None):
        """Log test results"""
        result = {
            "success": success,
            "message": message,
            "response_data": response_data
        }
        self.test_results[category][test_name] = result
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {category.upper()}: {test_name} - {message}")
        if not success and response_data:
            print(f"   Response: {response_data}")
    
    def log_error(self, error_message):
        """Log critical errors"""
        self.test_results["errors"].append(error_message)
        print(f"🚨 ERROR: {error_message}")
    
    def test_root_endpoint(self):
        """Test the root API endpoint"""
        try:
            response = requests.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                if "Brigada Paulista" in data.get("message", ""):
                    self.log_result("authentication", "root_endpoint", True, "Root endpoint working with correct message")
                else:
                    self.log_result("authentication", "root_endpoint", False, "Root endpoint message incorrect", data)
            else:
                self.log_result("authentication", "root_endpoint", False, f"Root endpoint returned {response.status_code}", response.text)
        except Exception as e:
            self.log_error(f"Root endpoint test failed: {str(e)}")
    
    def test_user_registration(self):
        """Test user registration"""
        try:
            # Test first user registration
            payload = {
                "username": TEST_USERNAME,
                "password": TEST_PASSWORD
            }
            response = requests.post(f"{self.base_url}/register", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and data.get("username") == TEST_USERNAME:
                    self.auth_token = data["access_token"]
                    self.log_result("authentication", "user_registration", True, "User registration successful with JWT token")
                else:
                    self.log_result("authentication", "user_registration", False, "Registration response missing token or username", data)
            else:
                self.log_result("authentication", "user_registration", False, f"Registration failed with status {response.status_code}", response.text)
            
            # Test second user registration
            payload_2 = {
                "username": TEST_USERNAME_2,
                "password": TEST_PASSWORD_2
            }
            response_2 = requests.post(f"{self.base_url}/register", json=payload_2)
            
            if response_2.status_code == 200:
                data_2 = response_2.json()
                if "access_token" in data_2:
                    self.auth_token_2 = data_2["access_token"]
                    self.log_result("authentication", "user_registration_2", True, "Second user registration successful")
                else:
                    self.log_result("authentication", "user_registration_2", False, "Second registration missing token", data_2)
            
            # Test duplicate username registration
            response_dup = requests.post(f"{self.base_url}/register", json=payload)
            if response_dup.status_code == 400:
                self.log_result("authentication", "duplicate_registration", True, "Duplicate registration properly rejected")
            else:
                self.log_result("authentication", "duplicate_registration", False, f"Duplicate registration not rejected: {response_dup.status_code}")
                
        except Exception as e:
            self.log_error(f"User registration test failed: {str(e)}")
    
    def test_user_login(self):
        """Test user login"""
        try:
            payload = {
                "username": TEST_USERNAME,
                "password": TEST_PASSWORD
            }
            response = requests.post(f"{self.base_url}/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and data.get("username") == TEST_USERNAME:
                    # Update token from login
                    self.auth_token = data["access_token"]
                    self.log_result("authentication", "user_login", True, "User login successful with JWT token")
                else:
                    self.log_result("authentication", "user_login", False, "Login response missing token or username", data)
            else:
                self.log_result("authentication", "user_login", False, f"Login failed with status {response.status_code}", response.text)
            
            # Test invalid credentials
            invalid_payload = {
                "username": TEST_USERNAME,
                "password": "senha_errada"
            }
            response_invalid = requests.post(f"{self.base_url}/login", json=invalid_payload)
            if response_invalid.status_code == 401:
                self.log_result("authentication", "invalid_login", True, "Invalid credentials properly rejected")
            else:
                self.log_result("authentication", "invalid_login", False, f"Invalid login not rejected: {response_invalid.status_code}")
                
        except Exception as e:
            self.log_error(f"User login test failed: {str(e)}")
    
    def test_get_current_user(self):
        """Test getting current user info with JWT"""
        try:
            if not self.auth_token:
                self.log_result("authentication", "get_current_user", False, "No auth token available for testing")
                return
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = requests.get(f"{self.base_url}/me", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("username") == TEST_USERNAME:
                    self.log_result("authentication", "get_current_user", True, "Current user info retrieved successfully")
                else:
                    self.log_result("authentication", "get_current_user", False, "Current user info incorrect", data)
            else:
                self.log_result("authentication", "get_current_user", False, f"Get current user failed: {response.status_code}", response.text)
            
            # Test without token
            response_no_token = requests.get(f"{self.base_url}/me")
            if response_no_token.status_code == 401:
                self.log_result("authentication", "get_current_user_no_token", True, "Unauthorized access properly rejected")
            else:
                self.log_result("authentication", "get_current_user_no_token", False, f"Unauthorized access not rejected: {response_no_token.status_code}")
                
        except Exception as e:
            self.log_error(f"Get current user test failed: {str(e)}")
    
    def test_create_thread_anonymous(self):
        """Test creating thread anonymously"""
        try:
            payload = {
                "title": "Revolução Constitucionalista de 1932",
                "content": "Companheiros paulistas, chegou a hora de relembrarmos os heróis de 32 que lutaram pela autonomia de São Paulo. MMDC nunca será esquecido!"
            }
            response = requests.post(f"{self.base_url}/threads", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "thread_id" in data:
                    self.test_thread_id = data["thread_id"]
                    self.log_result("forum", "create_thread_anonymous", True, "Anonymous thread creation successful")
                else:
                    self.log_result("forum", "create_thread_anonymous", False, "Thread creation response missing thread_id", data)
            else:
                self.log_result("forum", "create_thread_anonymous", False, f"Anonymous thread creation failed: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_error(f"Anonymous thread creation test failed: {str(e)}")
    
    def test_create_thread_authenticated(self):
        """Test creating thread with authentication"""
        try:
            if not self.auth_token:
                self.log_result("forum", "create_thread_authenticated", False, "No auth token available for testing")
                return
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            payload = {
                "title": "São Paulo Estado Livre - Nossa Bandeira",
                "content": "Irmãos bandeirantes, nossa bandeira tremula com orgulho! As cores preto, branco e vermelho representam nossa luta pela independência paulista."
            }
            response = requests.post(f"{self.base_url}/threads", json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "thread_id" in data:
                    self.log_result("forum", "create_thread_authenticated", True, "Authenticated thread creation successful")
                else:
                    self.log_result("forum", "create_thread_authenticated", False, "Authenticated thread creation response missing thread_id", data)
            else:
                self.log_result("forum", "create_thread_authenticated", False, f"Authenticated thread creation failed: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_error(f"Authenticated thread creation test failed: {str(e)}")
    
    def test_get_threads(self):
        """Test getting list of threads"""
        try:
            response = requests.get(f"{self.base_url}/threads")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    # Check if our test thread is in the list
                    thread_found = False
                    for thread in data:
                        if thread.get("id") == self.test_thread_id:
                            thread_found = True
                            break
                    
                    if thread_found or not self.test_thread_id:
                        self.log_result("forum", "get_threads", True, f"Thread list retrieved successfully ({len(data)} threads)")
                    else:
                        self.log_result("forum", "get_threads", False, "Test thread not found in thread list", data)
                else:
                    self.log_result("forum", "get_threads", True, "Thread list retrieved (empty list)")
            else:
                self.log_result("forum", "get_threads", False, f"Get threads failed: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_error(f"Get threads test failed: {str(e)}")
    
    def test_get_specific_thread(self):
        """Test getting specific thread details"""
        try:
            if not self.test_thread_id:
                self.log_result("forum", "get_specific_thread", False, "No test thread ID available")
                return
            
            response = requests.get(f"{self.base_url}/threads/{self.test_thread_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("id") == self.test_thread_id and "title" in data and "content" in data:
                    self.log_result("forum", "get_specific_thread", True, "Specific thread retrieved successfully")
                else:
                    self.log_result("forum", "get_specific_thread", False, "Thread data incomplete", data)
            else:
                self.log_result("forum", "get_specific_thread", False, f"Get specific thread failed: {response.status_code}", response.text)
            
            # Test non-existent thread
            response_404 = requests.get(f"{self.base_url}/threads/non-existent-id")
            if response_404.status_code == 404:
                self.log_result("forum", "get_nonexistent_thread", True, "Non-existent thread properly returns 404")
            else:
                self.log_result("forum", "get_nonexistent_thread", False, f"Non-existent thread returned: {response_404.status_code}")
                
        except Exception as e:
            self.log_error(f"Get specific thread test failed: {str(e)}")
    
    def test_create_reply_anonymous(self):
        """Test creating anonymous reply"""
        try:
            if not self.test_thread_id:
                self.log_result("forum", "create_reply_anonymous", False, "No test thread ID available")
                return
            
            payload = {
                "content": "Concordo plenamente! A Revolução de 32 foi um marco na história paulista. Viva São Paulo livre!"
            }
            response = requests.post(f"{self.base_url}/threads/{self.test_thread_id}/replies", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "reply_id" in data:
                    self.log_result("forum", "create_reply_anonymous", True, "Anonymous reply creation successful")
                else:
                    self.log_result("forum", "create_reply_anonymous", False, "Reply creation response missing reply_id", data)
            else:
                self.log_result("forum", "create_reply_anonymous", False, f"Anonymous reply creation failed: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_error(f"Anonymous reply creation test failed: {str(e)}")
    
    def test_create_reply_authenticated(self):
        """Test creating authenticated reply"""
        try:
            if not self.test_thread_id:
                self.log_result("forum", "create_reply_authenticated", False, "No test thread ID available")
                return
            
            if not self.auth_token_2:
                self.log_result("forum", "create_reply_authenticated", False, "No auth token available for testing")
                return
            
            headers = {"Authorization": f"Bearer {self.auth_token_2}"}
            payload = {
                "content": "Como bandeirante descendente, apoio totalmente a causa paulista. Nossa terra merece autonomia!"
            }
            response = requests.post(f"{self.base_url}/threads/{self.test_thread_id}/replies", json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "reply_id" in data:
                    self.log_result("forum", "create_reply_authenticated", True, "Authenticated reply creation successful")
                else:
                    self.log_result("forum", "create_reply_authenticated", False, "Authenticated reply creation response missing reply_id", data)
            else:
                self.log_result("forum", "create_reply_authenticated", False, f"Authenticated reply creation failed: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_error(f"Authenticated reply creation test failed: {str(e)}")
    
    def test_get_replies(self):
        """Test getting replies for a thread"""
        try:
            if not self.test_thread_id:
                self.log_result("forum", "get_replies", False, "No test thread ID available")
                return
            
            response = requests.get(f"{self.base_url}/threads/{self.test_thread_id}/replies")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("forum", "get_replies", True, f"Replies retrieved successfully ({len(data)} replies)")
                else:
                    self.log_result("forum", "get_replies", False, "Replies response not a list", data)
            else:
                self.log_result("forum", "get_replies", False, f"Get replies failed: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_error(f"Get replies test failed: {str(e)}")
    
    def test_image_upload(self):
        """Test image upload functionality"""
        try:
            # Create a simple test image
            img = Image.new('RGB', (100, 100), color='red')
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            files = {
                'file': ('test_image.png', img_buffer, 'image/png')
            }
            
            response = requests.post(f"{self.base_url}/upload-image", files=files)
            
            if response.status_code == 200:
                data = response.json()
                if "image_data" in data and "filename" in data:
                    # Verify base64 data is valid
                    try:
                        base64.b64decode(data["image_data"])
                        self.log_result("image_upload", "upload_image", True, "Image upload and base64 conversion successful")
                    except Exception:
                        self.log_result("image_upload", "upload_image", False, "Invalid base64 data returned", data)
                else:
                    self.log_result("image_upload", "upload_image", False, "Image upload response missing required fields", data)
            else:
                self.log_result("image_upload", "upload_image", False, f"Image upload failed: {response.status_code}", response.text)
            
            # Test invalid file type
            text_buffer = io.BytesIO(b"This is not an image")
            files_invalid = {
                'file': ('test.txt', text_buffer, 'text/plain')
            }
            
            response_invalid = requests.post(f"{self.base_url}/upload-image", files=files_invalid)
            if response_invalid.status_code == 400:
                self.log_result("image_upload", "upload_invalid_file", True, "Invalid file type properly rejected")
            else:
                self.log_result("image_upload", "upload_invalid_file", False, f"Invalid file type not rejected: {response_invalid.status_code}")
                
        except Exception as e:
            self.log_error(f"Image upload test failed: {str(e)}")
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Brigada Paulista Backend API Tests")
        print("=" * 60)
        
        # Test authentication system
        print("\n🔐 TESTING AUTHENTICATION SYSTEM")
        self.test_root_endpoint()
        self.test_user_registration()
        self.test_user_login()
        self.test_get_current_user()
        
        # Test forum API
        print("\n💬 TESTING FORUM API")
        self.test_create_thread_anonymous()
        self.test_create_thread_authenticated()
        self.test_get_threads()
        self.test_get_specific_thread()
        self.test_create_reply_anonymous()
        self.test_create_reply_authenticated()
        self.test_get_replies()
        
        # Test image upload
        print("\n🖼️ TESTING IMAGE UPLOAD")
        self.test_image_upload()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = 0
        passed_tests = 0
        
        for category, tests in self.test_results.items():
            if category == "errors":
                continue
            
            print(f"\n{category.upper()}:")
            for test_name, result in tests.items():
                total_tests += 1
                if result["success"]:
                    passed_tests += 1
                    print(f"  ✅ {test_name}")
                else:
                    print(f"  ❌ {test_name}: {result['message']}")
        
        if self.test_results["errors"]:
            print(f"\n🚨 CRITICAL ERRORS:")
            for error in self.test_results["errors"]:
                print(f"  • {error}")
        
        print(f"\n📈 RESULTS: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests*100):.1f}%)")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED!")
        else:
            print("⚠️  Some tests failed - check details above")

if __name__ == "__main__":
    tester = BrigadaPaulistaAPITester()
    tester.run_all_tests()