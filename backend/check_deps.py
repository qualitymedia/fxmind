mods = [
    'pymongo', 'fastapi', 'uvicorn', 'yfinance',
    'pandas', 'catboost', 'sklearn', 'pydantic', 'pydantic_settings',
    'pyarrow', 'websockets', 'structlog', 'watchfiles', 'httpx',
    'jose', 'passlib', 'yaml', 'numpy', 'scipy', 'joblib',
    'multipart', 'dotenv',
]
for m in mods:
    try:
        mod = __import__(m)
        ver = getattr(mod, '__version__', 'ok')
        print(f'  OK      {m}: {ver}')
    except ImportError as e:
        print(f'  MISSING {m}: {e}')
