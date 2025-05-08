import json
import urllib.parse
import requests
import random
import string
import time
import hashlib
import hmac
import base64


class VivoGPT:
    def __init__(self, app_id, app_key, uri="", domain="api-ai.vivo.com.cn", method="POST"):
        self.app_id = app_id
        self.app_key = app_key
        self.uri = uri
        self.domain = domain
        self.method = method

    # 随机字符串
    def gen_nonce(self, length=8):
        chars = string.ascii_lowercase + string.digits
        return ''.join([random.choice(chars) for _ in range(length)])

    def gen_canonical_query_string(self, params):
        if params:
            escape_uri = urllib.parse.quote
            raw = []
            for k in sorted(params.keys()):
                tmp_tuple = (escape_uri(k), escape_uri(str(params[k])))
                raw.append(tmp_tuple)
            s = "&".join("=".join(kv) for kv in raw)
            return s
        else:
            return ''

    def gen_signature(self, signing_string):
        bytes_secret = self.app_key.encode('utf-8')
        hash_obj = hmac.new(bytes_secret, signing_string, hashlib.sha256)
        bytes_sig = base64.b64encode(hash_obj.digest())
        signature = str(bytes_sig, encoding='utf-8')
        return signature

    def gen_sign_headers(self, query):
        method = str(self.method).upper()
        timestamp = str(int(time.time()))
        nonce = self.gen_nonce()
        canonical_query_string = self.gen_canonical_query_string(query)
        signed_headers_string = 'x-ai-gateway-app-id:{}\nx-ai-gateway-timestamp:{}\n' \
                                'x-ai-gateway-nonce:{}'.format(self.app_id, timestamp, nonce)
        signing_string = '{}\n{}\n{}\n{}\n{}\n{}'.format(method,
                                                         self.uri,
                                                         canonical_query_string,
                                                         self.app_id,
                                                         timestamp,
                                                         signed_headers_string)
        signing_string = signing_string.encode('utf-8')
        signature = self.gen_signature(signing_string)
        headers = {
            'X-AI-GATEWAY-APP-ID': self.app_id,
            'X-AI-GATEWAY-TIMESTAMP': timestamp,
            'X-AI-GATEWAY-NONCE': nonce,
            'X-AI-GATEWAY-SIGNED-HEADERS': "x-ai-gateway-app-id;x-ai-gateway-timestamp;x-ai-gateway-nonce",
            'X-AI-GATEWAY-SIGNATURE': signature,
            'Content-Type': 'application/json'
        }
        return headers

    async def stream_vivogpt(self, params, data):
        self.uri = "/vivogpt/completions/stream"
        headers = self.gen_sign_headers(params)
        headers['Content-Type'] = 'application/json'
        start_time = time.time()
        url = 'http://{}{}'.format(self.domain, self.uri)
        try:
            with requests.post(url, json=data, headers=headers, params=params, stream=True) as response:
                response.raise_for_status()  # Raise an exception for bad status codes
                first_line = True
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8', errors='ignore')
                        if first_line:
                            first_line = False
                            fl_time = time.time()
                            fl_timecost = fl_time - start_time
                            print("首字耗时: %.2f秒" % fl_timecost)
                        if "data:" not in decoded_line:
                            continue
                        print(f'decoded_line:{decoded_line}\t{decoded_line.split("data:")}')
                        try:
                            json_str = decoded_line.split("data:")[1]
                            res = json.loads(json_str)
                            chunk = {
                                "id": f"chatcmpl-{time.time()}",
                                "object": "chat.completion.chunk",
                                "created": int(time.time()),
                                "model": data.get("model", ""),
                                "choices": [{"delta": {"content": res['message']}, "index": 0, "finish_reason": None}],
                            }
                        except Exception as e:
                            chunk = {
                                "id": f"chatcmpl-{time.time()}",
                                "object": "chat.completion.chunk",
                                "created": int(time.time()),
                                "model": data.get("model", ""),
                                "choices": [{"delta": {}, "index": 0, "finish_reason": str(e)}],
                            }
                        yield f"data: {json.dumps(chunk)}\n\n"
                    yield f"data: {json.dumps({'id': f'chatcmpl-{time.time()}-final', 'object': 'chat.completion.chunk', 'created': int(time.time()), 'model': 'mock-gpt-model', 'choices': [{'delta': {}, 'index': 0, 'finish_reason': 'stop'}]})}\n\n"
        except requests.exceptions.RequestException as e:
            print(f"Error during request: {e}")
            raise e

    def vivogpt(self, params, data):
        self.uri = "/vivogpt/completions"
        headers = self.gen_sign_headers(params)
        headers['Content-Type'] = 'application/json'
        url = 'http://{}{}'.format(self.domain, self.uri)
        try:
            response = requests.post(url, json=data, headers=headers, params=params, stream=True)
            json_res = response.json()
            res_data = json_res.get('data', {})
            print()
            res = {
                "id": res_data.get("sessionId", ""),
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": res_data.get("model", ""),
                "choices": [{
                    "message": {"role": "assistant", "content": res_data.get('content', '')}
                }]
            }
            return res
        except Exception as e:
            print(f"Error during request: {e}")
            raise e
