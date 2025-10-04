#!/usr/bin/env python3
"""
Field-Level Encryption Utility

This module provides field-level encryption for sensitive personal information:
- User photos and profile images
- Email addresses
- Personal preferences
- User metadata
- Profile information

Uses AES-256-GCM for authenticated encryption with unique keys per field.
"""

import os
import base64
import json
import hashlib
from typing import Dict, Any, Optional, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class EncryptionError(Exception):
    """Custom exception for encryption errors."""
    pass

class FieldEncryptor:
    """Field-level encryption for sensitive personal data."""
    
    def __init__(self, master_key: Optional[str] = None):
        """
        Initialize the field encryptor.
        
        Args:
            master_key: Master encryption key (if not provided, will be generated)
        """
        self.master_key = master_key or self._generate_master_key()
        self.backend = default_backend()
        
        # Fields that should be encrypted
        self.encrypted_fields = {
            'email',
            'phone',
            'address',
            'personal_notes',
            'profile_image_url',
            'avatar_url',
            'user_photos',
            'preferences.personal',
            'measurements.personal',
            'metadata.personal'
        }
        
        # Fields that should NOT be encrypted (wardrobe items, etc.)
        self.excluded_fields = {
            'wardrobe',
            'outfits',
            'analytics',
            'trends',
            'public_data'
        }
    
    def _generate_master_key(self) -> str:
        """Generate a secure master key."""
        return base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')
    
    def _derive_field_key(self, field_name: str, user_id: str) -> bytes:
        """Derive a unique encryption key for a specific field and user."""
        # Create a unique salt for each field-user combination
        salt = hashlib.sha256(f"{field_name}:{user_id}".encode()).digest()
        
        # Derive key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=self.backend
        )
        
        key = kdf.derive(self.master_key.encode())
        return key
    
    def _should_encrypt_field(self, field_path: str) -> bool:
        """Check if a field should be encrypted."""
        # Check if field is in excluded list
        for excluded in self.excluded_fields:
            if excluded in field_path:
                return False
        
        # Check if field is in encrypted list
        for encrypted in self.encrypted_fields:
            if encrypted in field_path:
                return True
        
        # Default: don't encrypt
        return False
    
    def encrypt_field(self, value: Any, field_name: str, user_id: str) -> Dict[str, str]:
        """
        Encrypt a single field value.
        
        Args:
            value: Value to encrypt
            field_name: Name of the field
            user_id: User ID for key derivation
            
        Returns:
            Dict with encrypted data and metadata
        """
        try:
            if not self._should_encrypt_field(field_name):
                return {"value": value, "encrypted": False}
            
            # Convert value to string if needed
            if not isinstance(value, str):
                value = json.dumps(value)
            
            # Derive field-specific key
            key = self._derive_field_key(field_name, user_id)
            
            # Generate random IV
            iv = os.urandom(16)
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(iv),
                backend=self.backend
            )
            
            encryptor = cipher.encryptor()
            
            # Pad the data
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(value.encode()) + padder.finalize()
            
            # Encrypt
            ciphertext = encryptor.update(padded_data) + encryptor.finalize()
            
            # Get tag for authentication
            tag = encryptor.tag
            
            # Combine IV, ciphertext, and tag
            encrypted_data = iv + ciphertext + tag
            
            # Encode as base64
            encrypted_b64 = base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
            
            return {
                "value": encrypted_b64,
                "encrypted": True,
                "field_name": field_name,
                "encryption_method": "AES-256-GCM",
                "encrypted_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to encrypt field {field_name}: {e}")
            raise EncryptionError(f"Encryption failed for field {field_name}: {str(e)}")
    
    def decrypt_field(self, encrypted_data: Dict[str, Any], field_name: str, user_id: str) -> Any:
        """
        Decrypt a single field value.
        
        Args:
            encrypted_data: Dict containing encrypted data
            field_name: Name of the field
            user_id: User ID for key derivation
            
        Returns:
            Decrypted value
        """
        try:
            if not (encrypted_data.get("encrypted", False) if encrypted_data else False):
                return (encrypted_data.get("value") if encrypted_data else None)
            
            # Get encrypted value
            encrypted_b64 = encrypted_data["value"]
            encrypted_data_bytes = base64.urlsafe_b64decode(encrypted_b64)
            
            # Extract IV, ciphertext, and tag
            iv = encrypted_data_bytes[:16]
            tag = encrypted_data_bytes[-16:]
            ciphertext = encrypted_data_bytes[16:-16]
            
            # Derive field-specific key
            key = self._derive_field_key(field_name, user_id)
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(iv, tag),
                backend=self.backend
            )
            
            decryptor = cipher.decryptor()
            
            # Decrypt
            padded_data = decryptor.update(ciphertext) + decryptor.finalize()
            
            # Unpad
            unpadder = padding.PKCS7(128).unpadder()
            data = unpadder.update(padded_data) + unpadder.finalize()
            
            # Try to parse as JSON, fallback to string
            try:
                return json.loads(data.decode())
            except json.JSONDecodeError:
                return data.decode()
            
        except Exception as e:
            logger.error(f"Failed to decrypt field {field_name}: {e}")
            raise EncryptionError(f"Decryption failed for field {field_name}: {str(e)}")
    
    def encrypt_user_data(self, user_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Encrypt sensitive fields in user data.
        
        Args:
            user_data: User data dictionary
            user_id: User ID
            
        Returns:
            User data with sensitive fields encrypted
        """
        encrypted_data = {}
        
        for field_name, value in user_data.items():
            if self._should_encrypt_field(field_name):
                encrypted_data[field_name] = self.encrypt_field(value, field_name, user_id)
            else:
                encrypted_data[field_name] = value
        
        return encrypted_data
    
    def decrypt_user_data(self, user_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Decrypt sensitive fields in user data.
        
        Args:
            user_data: User data dictionary with encrypted fields
            user_id: User ID
            
        Returns:
            User data with sensitive fields decrypted
        """
        decrypted_data = {}
        
        for field_name, value in user_data.items():
            if isinstance(value, dict) and (value.get("encrypted", False) if value else False):
                decrypted_data[field_name] = self.decrypt_field(value, field_name, user_id)
            else:
                decrypted_data[field_name] = value
        
        return decrypted_data
    
    def encrypt_profile_image(self, image_url: str, user_id: str) -> Dict[str, str]:
        """
        Encrypt a profile image URL.
        
        Args:
            image_url: URL of the profile image
            user_id: User ID
            
        Returns:
            Encrypted image data
        """
        return self.encrypt_field(image_url, "profile_image_url", user_id)
    
    def decrypt_profile_image(self, encrypted_data: Dict[str, Any], user_id: str) -> str:
        """
        Decrypt a profile image URL.
        
        Args:
            encrypted_data: Encrypted image data
            user_id: User ID
            
        Returns:
            Decrypted image URL
        """
        return self.decrypt_field(encrypted_data, "profile_image_url", user_id)
    
    def encrypt_email(self, email: str, user_id: str) -> Dict[str, str]:
        """
        Encrypt an email address.
        
        Args:
            email: Email address
            user_id: User ID
            
        Returns:
            Encrypted email data
        """
        return self.encrypt_field(email, "email", user_id)
    
    def decrypt_email(self, encrypted_data: Dict[str, Any], user_id: str) -> str:
        """
        Decrypt an email address.
        
        Args:
            encrypted_data: Encrypted email data
            user_id: User ID
            
        Returns:
            Decrypted email address
        """
        return self.decrypt_field(encrypted_data, "email", user_id)

# Global encryptor instance
_encryptor = None

def get_encryptor() -> FieldEncryptor:
    """Get the global encryptor instance."""
    global _encryptor
    if _encryptor is None:
        # Get master key from environment variable
        master_key = os.getenv("ENCRYPTION_MASTER_KEY")
        _encryptor = FieldEncryptor(master_key)
    return _encryptor

def encrypt_sensitive_data(data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """
    Convenience function to encrypt sensitive data.
    
    Args:
        data: Data to encrypt
        user_id: User ID
        
    Returns:
        Data with sensitive fields encrypted
    """
    encryptor = get_encryptor()
    return encryptor.encrypt_user_data(data, user_id)

def decrypt_sensitive_data(data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """
    Convenience function to decrypt sensitive data.
    
    Args:
        data: Data to decrypt
        user_id: User ID
        
    Returns:
        Data with sensitive fields decrypted
    """
    encryptor = get_encryptor()
    return encryptor.decrypt_user_data(data, user_id)

# Example usage:
if __name__ == "__main__":
    # Test the encryption
    encryptor = FieldEncryptor()
    
    test_user_id = "test_user_123"
    test_data = {
        "email": "user@example.com",
        "profile_image_url": "https://example.com/profile.jpg",
        "wardrobe_items": ["item1", "item2"],  # Should not be encrypted
        "personal_notes": "Private notes about user"
    }
    
    print("Original data:", test_data)
    
    # Encrypt sensitive data
    encrypted_data = encryptor.encrypt_user_data(test_data, test_user_id)
    print("Encrypted data:", encrypted_data)
    
    # Decrypt sensitive data
    decrypted_data = encryptor.decrypt_user_data(encrypted_data, test_user_id)
    print("Decrypted data:", decrypted_data)
    
    # Verify data matches
    assert test_data["email"] == decrypted_data["email"]
    assert test_data["profile_image_url"] == decrypted_data["profile_image_url"]
    assert test_data["wardrobe_items"] == decrypted_data["wardrobe_items"]
    assert test_data["personal_notes"] == decrypted_data["personal_notes"]
    
    print("✅ Encryption/decryption test passed!") 