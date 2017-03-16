import hashlib
import uuid
algorithm = 'sha512'
password = 'rebeccapass15'
salt = uuid.uuid4().hex

m = hashlib.new(algorithm)
m.update(str(salt+password).encode('utf-8'))
password_hash = m.hexdigest()

print ("$".join([algorithm,salt,password_hash]))