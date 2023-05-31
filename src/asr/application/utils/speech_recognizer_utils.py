from datetime import datetime

def build_file_name(base_file_name: str, ext: str) -> str:
    suffix = datetime.utcnow().strftime(r'%m%d%Y%H%M%S%f')
    file_name = f'{base_file_name}_{suffix}.{ext}'

    return file_name
