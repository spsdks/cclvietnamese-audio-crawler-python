import regex as re
import requests
import json
import os
import copy

session_url = "https://naati.assessmentq.com/api/Session/"
assets_url = "https://naati.assessmentq.com/api/Session/{session_token}?isReview=false&includeMetadata=false"
media_url = 'https://cdn-media3.assessmentq.com/33593221-DFFD-4691-BD05-445BC2B45F3A/download/{access_code}?method={method}'

code_regex = r"userAccessCode=(?P<user_access_code>[a-z0-9\-]+).*treeStructureAccessCode=(?P<tree_access_code>[a-z0-9\-]+)"
token_regex = r"window\.startupData = \{.*\"token\":\"(?P<token>[^\"]+)\""

token_headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'}
session_headers = {
    'Authorization': 'Bearer {token}',
    'Content-Type': 'application/json; charset=utf-8'
}
media_headers = {
    'X-Preload': 'true'
}

def get_code(url):
    code = re.search(code_regex, url)

    user_access_code = code.group('user_access_code')
    tree_access_code = code.group('tree_access_code')
    
    return user_access_code, tree_access_code

def get_token(url):
    response = requests.request("GET", url, headers=token_headers)
    html = re.search(token_regex, response.text, flags = re.DOTALL)
    token = html.group('token')
    return token

def get_session_header(token):
    headers = copy.deepcopy(session_headers)
    headers['Authorization'] = headers['Authorization'].format(token = token)

    return headers

def get_session_token(tree_access_code, token):
    headers = get_session_header(token)
    
    data = f'{{\r\n    \"publicationAccessCode\":\"{tree_access_code}\",\r\n}}'
    response = requests.request("POST", session_url, headers=headers, data=data)
    session_token = response.text[1:-1]
    
    return session_token

def get_assets(session_token, token):
    headers = get_session_header(token)
    response = requests.request("GET", assets_url.format(session_token=session_token), headers=headers)

    nodes = json.loads(response.text)["tree"]["treeNode"]["childTreeNodes"]
    assets = []
    for node in nodes:
        for child_node in node['childTreeNodes']:
            for asset in child_node['binaryAssets']:
                if 'binaryAssetFile' not in asset:
                    continue

                asset_file = asset['binaryAssetFile']
                if 'binaryAssetExtension' not in asset_file:
                    continue

                assets.append({
                    'access_code': asset['accessCode'],
                    'name': asset['name'],
                    'method': asset['name'].split(".")[-1],
                    'link': media_url.format(
                        access_code = asset['accessCode'],
                        method = asset['name'].split(".")[-1]
                    )
                })
    
    return assets

def process_url(url, path = "assets"):
    user_access_code, tree_access_code = get_code(url)
    token = get_token(url)
    session_token = get_session_token(tree_access_code, token)
    assets = get_assets(session_token, token)

    save_path = os.path.join(path, tree_access_code)
    
    links = [asset['link'] for asset in assets]
    file_names = [asset['name'] for asset in assets]

    return [(url, file_name, save_path) for url, file_name in zip(links, file_names)], save_path


async def aprocess_url(url, path = "assets"):
    user_access_code, tree_access_code = get_code(url)
    token = get_token(url)
    session_token = get_session_token(tree_access_code, token)
    assets = get_assets(session_token, token)

    save_path = os.path.join(path, tree_access_code)
    
    links = [asset['link'] for asset in assets]
    file_names = [asset['name'] for asset in assets]

    return [(url, file_name, save_path) for url, file_name in zip(links, file_names)], save_path

def download_file(data):
    url, file_name, save_path = data

    with requests.get(url, headers=media_headers, stream=True) as r:
        r.raise_for_status()
        with open(os.path.join(save_path, file_name), 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

async def adownload_file(data):
    url, file_name, save_path = data

    with requests.get(url, headers=media_headers, stream=True) as r:
        r.raise_for_status()
        with open(os.path.join(save_path, file_name), 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)