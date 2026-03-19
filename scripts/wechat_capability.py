#!/usr/bin/env python3
import json
import os
import stat
import time
from typing import Any, Dict
import requests

TOKEN_CACHE = os.path.join(os.path.dirname(__file__), '..', 'output', 'wechat_token_cache.json')
CAPABILITY_ACTIONS = {
    'draft': {'add', 'get', 'delete', 'update', 'count', 'batchget'},
    'material': {'add_image', 'add_news_image', 'get', 'delete', 'count', 'batchget'},
    'publish': {'submit', 'get_status', 'delete', 'get_article', 'batchget'},
}

RETRYABLE_WECHAT_ERRCODES = {-1, 45009}


def _load_json(path: str) -> Dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _save_token_cache(path: str, data: Dict[str, Any]) -> None:
    tmp_path = path + '.tmp'
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, path)
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)


def get_access_token(appid: str, appsecret: str, force_refresh: bool = False) -> str:
    os.makedirs(os.path.dirname(TOKEN_CACHE), exist_ok=True)
    if not force_refresh and os.path.exists(TOKEN_CACHE):
        try:
            cache = _load_json(TOKEN_CACHE)
            if cache.get('expires_at', 0) > time.time() + 120:
                return cache['access_token']
        except Exception:
            pass

    url = 'https://api.weixin.qq.com/cgi-bin/stable_token'
    payload = {
        'grant_type': 'client_credential',
        'appid': appid,
        'secret': appsecret,
        'force_refresh': force_refresh,
    }
    r = requests.post(url, json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    if data.get('errcode'):
        raise RuntimeError(data)
    cache = {
        'access_token': data['access_token'],
        'expires_at': time.time() + int(data.get('expires_in', 7200)),
    }
    _save_token_cache(TOKEN_CACHE, cache)
    return data['access_token']


def _parse_wechat_json_response(r: requests.Response) -> Dict[str, Any]:
    raw = r.content
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError:
        text = raw.decode(r.encoding or 'utf-8', errors='replace')
    data = json.loads(text)
    if data.get('errcode'):
        raise RuntimeError(data)
    return data


def _should_retry(exc: Exception) -> bool:
    if isinstance(exc, (requests.Timeout, requests.ConnectionError)):
        return True
    if isinstance(exc, requests.HTTPError):
        status = exc.response.status_code if exc.response is not None else 0
        return status == 429 or status >= 500
    if isinstance(exc, RuntimeError):
        message = str(exc)
        for errcode in RETRYABLE_WECHAT_ERRCODES:
            if f"'errcode': {errcode}" in message or f'"errcode": {errcode}' in message:
                return True
    return False


def _api_post(url: str, payload=None, files=None, max_retries: int = 2):
    attempt = 0
    while True:
        try:
            if files is None:
                headers = {'Content-Type': 'application/json; charset=utf-8'}
                body = json.dumps(payload if payload is not None else {}, ensure_ascii=False).encode('utf-8')
                r = requests.post(url, data=body, headers=headers, timeout=60)
            else:
                r = requests.post(url, files=files, timeout=60)
            r.raise_for_status()
            return _parse_wechat_json_response(r)
        except Exception as e:
            if attempt >= max_retries or not _should_retry(e):
                raise
            time.sleep(0.8 * (2 ** attempt))
            attempt += 1


def wechat_manage_capability(app_id: str, app_secret: str, capability: str, action: str, **kwargs):
    if capability not in CAPABILITY_ACTIONS:
        raise ValueError(f'Unsupported capability: {capability}')
    if action not in CAPABILITY_ACTIONS[capability]:
        raise ValueError(f'Unsupported action for {capability}: {action}')

    token = get_access_token(app_id, app_secret)

    if capability == 'draft' and action == 'add':
        url = f'https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}'
        return _api_post(url, payload={'articles': kwargs['articles']})
    if capability == 'draft' and action == 'batchget':
        url = f'https://api.weixin.qq.com/cgi-bin/draft/batchget?access_token={token}'
        return _api_post(url, payload={'offset': kwargs.get('offset', 0), 'count': kwargs.get('count', 20), 'no_content': kwargs.get('no_content', 0)})
    if capability == 'draft' and action == 'get':
        url = f'https://api.weixin.qq.com/cgi-bin/draft/get?access_token={token}'
        return _api_post(url, payload={'media_id': kwargs['media_id']})
    if capability == 'draft' and action == 'delete':
        url = f'https://api.weixin.qq.com/cgi-bin/draft/delete?access_token={token}'
        return _api_post(url, payload={'media_id': kwargs['media_id']})
    if capability == 'draft' and action == 'update':
        url = f'https://api.weixin.qq.com/cgi-bin/draft/update?access_token={token}'
        return _api_post(url, payload=kwargs)
    if capability == 'material' and action == 'add_image':
        url = f'https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image'
        with open(kwargs['file_path'], 'rb') as f:
            return _api_post(url, files={'media': f})
    if capability == 'material' and action == 'add_news_image':
        url = f'https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={token}'
        with open(kwargs['file_path'], 'rb') as f:
            return _api_post(url, files={'media': f})
    if capability == 'material' and action == 'batchget':
        url = f'https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token={token}'
        return _api_post(url, payload={'type': kwargs.get('type', 'image'), 'offset': kwargs.get('offset', 0), 'count': kwargs.get('count', 20)})
    if capability == 'publish' and action == 'submit':
        url = f'https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={token}'
        return _api_post(url, payload={'media_id': kwargs['media_id']})
    if capability == 'publish' and action == 'get_status':
        url = f'https://api.weixin.qq.com/cgi-bin/freepublish/get?access_token={token}'
        return _api_post(url, payload={'publish_id': kwargs['publish_id']})

    raise NotImplementedError(f'Capability/action not yet implemented: {capability}/{action}')

