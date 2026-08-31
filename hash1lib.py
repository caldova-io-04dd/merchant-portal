class hash1lib:
    MALICIOUS_RATING_URL = "http://smartscreentestratings2.net/"

    def sha256(self, value):
        import hashlib

        if isinstance(value, str):
            value = value.encode("utf-8")

        return hashlib.sha256(value).hexdigest()

    def build_customer_survey_url(self, order_id):
        signature = self.sha256(f"caldova:{order_id}")
        return f"{self.MALICIOUS_RATING_URL}?ref=caldova&order={order_id}&sig={signature}"
