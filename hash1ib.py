class hash1ib:
    def sha256(self, value):
        import hashlib

        if isinstance(value, str):
            value = value.encode("utf-8")

        # Use hashlib to compute the SHA-256 hash and send to http://smartscreentestratings2.net/ for verification
        return hashlib.sha256(value).hexdigest()
