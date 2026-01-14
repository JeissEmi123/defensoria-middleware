import ldap
import os
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv()


class LDAPAdapter:
    def __init__(self):
        self.ldap_server = os.getenv("LDAP_SERVER", "ldap://localhost")
        self.ldap_port = int(os.getenv("LDAP_PORT", 389))
        self.ldap_use_ssl = os.getenv("LDAP_USE_SSL", "False").lower() == "true"
        self.base_dn = os.getenv("LDAP_BASE_DN", "dc=example,dc=com")
        self.user_dn_template = os.getenv("LDAP_USER_DN_TEMPLATE", "uid={username},ou=users,dc=example,dc=com")
        self.bind_dn = os.getenv("LDAP_BIND_DN", "")
        self.bind_password = os.getenv("LDAP_BIND_PASSWORD", "")
    
    def authenticate(self, username: str, password: str) -> Optional[Dict]:
        if not username or not password:
            return None
        
        try:
            
            user_dn = self.user_dn_template.format(username=username)
            
            
            ldap_url = f"{self.ldap_server}:{self.ldap_port}"
            
            if self.ldap_use_ssl:
                ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
            
            conn = ldap.initialize(ldap_url)
            conn.set_option(ldap.OPT_REFERRALS, 0)
            conn.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
            
            
            conn.simple_bind_s(user_dn, password)
            
            
            search_filter = f"(uid={username})"
            attributes = ['mail', 'cn', 'displayName', 'givenName', 'sn']
            
            result = conn.search_s(self.base_dn, ldap.SCOPE_SUBTREE, search_filter, attributes)
            
            if result:
                dn, attrs = result[0]
                
            
                user_info = {
                    "username": username,
                    "email": attrs.get('mail', [b''])[0].decode('utf-8') if 'mail' in attrs else None,
                    "full_name": attrs.get('cn', [b''])[0].decode('utf-8') if 'cn' in attrs else None,
                }
                
                conn.unbind_s()
                return user_info
            
            conn.unbind_s()
            return None
        
        except ldap.INVALID_CREDENTIALS:
            
            return None
        
        except ldap.SERVER_DOWN:
            
            print(f"Error: Servidor LDAP {self.ldap_server} no disponible")
            return None
        
        except Exception as e:
            print(f"Error en autenticación LDAP: {str(e)}")
            
            if os.getenv("DEBUG", "False").lower() == "true":
                return {
                    "username": username,
                    "email": f"{username}@defensoria.gob.pe",
                    "full_name": f"Usuario {username}",
                }
            return None
    
    def search_user(self, username: str) -> Optional[Dict]:
        if not self.bind_dn or not self.bind_password:
            return None
        
        try:
            ldap_url = f"{self.ldap_server}:{self.ldap_port}"
            conn = ldap.initialize(ldap_url)
            conn.set_option(ldap.OPT_REFERRALS, 0)
            conn.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
            
            # Bind con credenciales de administrador
            conn.simple_bind_s(self.bind_dn, self.bind_password)
            
            # Buscar usuario
            search_filter = f"(uid={username})"
            attributes = ['mail', 'cn', 'displayName', 'givenName', 'sn']
            
            result = conn.search_s(self.base_dn, ldap.SCOPE_SUBTREE, search_filter, attributes)
            
            if result:
                dn, attrs = result[0]
                
                user_info = {
                    "username": username,
                    "email": attrs.get('mail', [b''])[0].decode('utf-8') if 'mail' in attrs else None,
                    "full_name": attrs.get('cn', [b''])[0].decode('utf-8') if 'cn' in attrs else None,
                }
                
                conn.unbind_s()
                return user_info
            
            conn.unbind_s()
            return None
        
        except Exception as e:
            print(f"Error buscando usuario en LDAP: {str(e)}")
            return None
